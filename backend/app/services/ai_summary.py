import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.session import Session
from app.models.health_snapshot import HealthSnapshot
from app.models.repo import Repo
from app.models.summary import Summary
from app.config import settings
from datetime import datetime, timedelta, timezone

genai.configure(api_key=settings.GEMINI_API_KEY)

async def generate_weekly_summary(db: AsyncSession):
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    res = await db.execute(select(Session).where(Session.started_at >= week_ago))
    sessions = res.scalars().all()
    
    total_seconds = sum(s.duration_seconds for s in sessions)
    total_hours = total_seconds / 3600
    total_sessions = len(sessions)
    avg_session = (total_seconds / total_sessions / 60) if total_sessions > 0 else 0
    
    proj_times = {}
    lang_times = {}
    
    for s in sessions:
        if s.project:
            proj_times[s.project] = proj_times.get(s.project, 0) + s.duration_seconds
        for lang, t in s.languages.items():
            lang_times[lang] = lang_times.get(lang, 0) + t
            
    top_projects = ", ".join([p for p, _ in sorted(proj_times.items(), key=lambda x: x[1], reverse=True)[:3]])
    top_languages = ", ".join([l for l, _ in sorted(lang_times.items(), key=lambda x: x[1], reverse=True)[:3]])
    
    repos_res = await db.execute(select(Repo))
    repos = repos_res.scalars().all()
    health_summaries = []
    for r in repos:
        snap_res = await db.execute(select(HealthSnapshot).where(HealthSnapshot.repo_id == r.id).order_by(HealthSnapshot.taken_at.desc()).limit(1))
        snap = snap_res.scalars().first()
        if snap:
            health_summaries.append(f"{r.name}: Score {snap.health_score}")
            
    health_summary = "; ".join(health_summaries) if health_summaries else "No data"
    
    prompt = f"""You are a developer productivity assistant. Here is a summary of a developer's past week:
Total coding time: {total_hours:.1f} hours across {total_sessions} sessions
Average session length: {avg_session:.0f} minutes
Top projects: {top_projects}
Top languages: {top_languages}
Codebase health: {health_summary}

Write a warm, insightful, 3-paragraph summary of their week.
Paragraph 1: what they focused on.
Paragraph 2: patterns or observations (positive or constructive).
Paragraph 3: one concrete suggestion for next week.
Keep it under 200 words. Be specific, not generic."""

    try:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
        except Exception:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
        content = response.text
    except Exception as e:
        content = f"Failed to generate summary: {str(e)}"
        
    last_monday = now.date() - timedelta(days=now.weekday())
    
    summary = Summary(
        week_start=last_monday,
        content=content
    )
    db.add(summary)
    await db.commit()
    
    return content
