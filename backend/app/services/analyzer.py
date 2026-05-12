import subprocess
import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.repo import Repo
from app.models.health_snapshot import HealthSnapshot
from .health_score import compute_health_score

async def analyze_repo(repo_id: str, db: AsyncSession):
    repo = await db.get(Repo, repo_id)
    if not repo:
        return
        
    path = repo.local_path
    if not os.path.exists(path):
        return
        
    coverage = 0.0
    try:
        subprocess.run(["pytest", "--cov=.", "--cov-report=json", "-q", "--tb=no"], cwd=path, capture_output=True)
        if os.path.exists(os.path.join(path, "coverage.json")):
            with open(os.path.join(path, "coverage.json")) as f:
                cov_data = json.load(f)
                coverage = float(cov_data.get("totals", {}).get("percent_covered", 0))
    except Exception:
        pass

    complexity = 0.0
    try:
        res = subprocess.run(["radon", "cc", ".", "-j"], cwd=path, capture_output=True, text=True)
        cc_data = json.loads(res.stdout)
        total_cc = 0
        count = 0
        for file_data in cc_data.values():
            if isinstance(file_data, list):
                for item in file_data:
                    if 'complexity' in item:
                        total_cc += item['complexity']
                        count += 1
        if count > 0:
            complexity = total_cc / count
    except Exception:
        pass

    dead_code_count = 0
    try:
        res = subprocess.run(["vulture", ".", "--min-confidence", "80"], cwd=path, capture_output=True, text=True)
        lines = res.stdout.strip().split('\n')
        dead_code_count = len([l for l in lines if l])
    except Exception:
        pass

    high_churn_files = []
    try:
        res = subprocess.run(["git", "log", "--since=30.days", "--numstat", "--pretty=format:"], cwd=path, capture_output=True, text=True)
        file_counts = {}
        for line in res.stdout.split('\n'):
            parts = line.split('\t')
            if len(parts) == 3:
                fname = parts[2]
                file_counts[fname] = file_counts.get(fname, 0) + 1
                
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for fname, churn in sorted_files:
            if churn > 10:
                high_churn_files.append({"file": fname, "churn_count": churn, "has_coverage": False})
    except Exception:
        pass

    score = compute_health_score(coverage, complexity, dead_code_count, len(high_churn_files))
    
    snapshot = HealthSnapshot(
        repo_id=repo_id,
        test_coverage=coverage,
        avg_complexity=complexity,
        dead_code_count=dead_code_count,
        high_churn_files=high_churn_files,
        health_score=score
    )
    db.add(snapshot)
    
    from datetime import datetime, timezone
    repo.last_analyzed = datetime.now(timezone.utc)
    
    await db.commit()
