from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.repo import Repo
from app.models.health_snapshot import HealthSnapshot
from app.schemas.repo import RepoCreate, RepoOut
from app.schemas.health_snapshot import HealthSnapshotOut
from app.services.analyzer import analyze_repo

router = APIRouter(prefix="/repos", tags=["repos"])

@router.post("", response_model=RepoOut)
async def create_repo(repo_in: RepoCreate, db: AsyncSession = Depends(get_db)):
    repo = Repo(name=repo_in.name, local_path=repo_in.local_path)
    db.add(repo)
    await db.commit()
    await db.refresh(repo)
    return repo

@router.get("", response_model=List[RepoOut])
async def list_repos(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Repo).order_by(Repo.created_at.desc()))
    repos = res.scalars().all()
    
    result = []
    for r in repos:
        snap_res = await db.execute(
            select(HealthSnapshot)
            .where(HealthSnapshot.repo_id == r.id)
            .order_by(HealthSnapshot.taken_at.desc())
            .limit(1)
        )
        snap = snap_res.scalars().first()
        
        repo_dict = {
            "id": r.id,
            "name": r.name,
            "local_path": r.local_path,
            "last_analyzed": r.last_analyzed,
            "created_at": r.created_at,
            "latest_snapshot": snap
        }
        result.append(repo_dict)
        
    return result

@router.post("/{repo_id}/analyze")
async def trigger_analysis(repo_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    repo = await db.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
        
    background_tasks.add_task(analyze_repo, repo_id, db)
    return {"status": "Analysis triggered"}

@router.get("/{repo_id}/health", response_model=List[HealthSnapshotOut])
async def get_repo_health(repo_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HealthSnapshot)
        .where(HealthSnapshot.repo_id == repo_id)
        .order_by(HealthSnapshot.taken_at.desc())
        .limit(10)
    )
    return res.scalars().all()
