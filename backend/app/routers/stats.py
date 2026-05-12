from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.database import get_db
from app.models.device import Device
from app.models.session import Session
from app.models.summary import Summary
from app.middleware.auth import get_current_device

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/heatmap")
async def get_heatmap(days: int = 90, db: AsyncSession = Depends(get_db), device: Device = Depends(get_current_device)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    res = await db.execute(
        select(func.date(Session.started_at).label('date'), func.sum(Session.duration_seconds).label('total_seconds'))
        .where(and_(Session.device_id == device.id, Session.started_at >= cutoff))
        .group_by('date')
    )
    
    results = []
    for row in res.all():
        results.append({
            "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
            "total_seconds": row.total_seconds
        })
    return results

@router.get("/languages")
async def get_languages(days: int = 30, project: Optional[str] = None, db: AsyncSession = Depends(get_db), device: Device = Depends(get_current_device)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    query = select(Session.languages).where(and_(Session.device_id == device.id, Session.started_at >= cutoff))
    if project:
        query = query.where(Session.project == project)
        
    res = await db.execute(query)
    
    lang_totals = {}
    for row in res.all():
        langs = row[0]
        for lang, secs in langs.items():
            lang_totals[lang] = lang_totals.get(lang, 0) + secs
            
    sorted_langs = [{"language": k, "seconds": v} for k, v in sorted(lang_totals.items(), key=lambda item: item[1], reverse=True)]
    return sorted_langs

@router.get("/projects")
async def get_projects(days: int = 30, db: AsyncSession = Depends(get_db), device: Device = Depends(get_current_device)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    res = await db.execute(
        select(Session)
        .where(and_(Session.device_id == device.id, Session.started_at >= cutoff))
    )
    sessions = res.scalars().all()
    
    proj_stats = {}
    for s in sessions:
        p = s.project or "Unknown"
        if p not in proj_stats:
            proj_stats[p] = {"total_seconds": 0, "last_active": s.ended_at, "session_count": 0, "langs": {}}
        
        ps = proj_stats[p]
        ps["total_seconds"] += s.duration_seconds
        ps["session_count"] += 1
        if s.ended_at > ps["last_active"]:
            ps["last_active"] = s.ended_at
            
        for lang, secs in s.languages.items():
            ps["langs"][lang] = ps["langs"].get(lang, 0) + secs
            
    results = []
    for p, stats in proj_stats.items():
        top_lang = max(stats["langs"].items(), key=lambda x: x[1])[0] if stats["langs"] else "Unknown"
        results.append({
            "project": p,
            "total_seconds": stats["total_seconds"],
            "last_active": stats["last_active"].isoformat(),
            "session_count": stats["session_count"],
            "top_language": top_lang
        })
        
    return sorted(results, key=lambda x: x["last_active"], reverse=True)

@router.get("/focus")
async def get_focus(days: int = 30, db: AsyncSession = Depends(get_db), device: Device = Depends(get_current_device)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    res = await db.execute(
        select(Session)
        .where(and_(Session.device_id == device.id, Session.started_at >= cutoff))
        .order_by(Session.started_at.asc())
    )
    sessions = res.scalars().all()
    
    total_sessions = len(sessions)
    if total_sessions == 0:
        return {
            "avg_session_seconds": 0,
            "longest_session_seconds": 0,
            "total_sessions": 0,
            "avg_sessions_per_day": 0,
            "context_switches": 0
        }
        
    total_seconds = sum(s.duration_seconds for s in sessions)
    longest = max(s.duration_seconds for s in sessions)
    avg = total_seconds / total_sessions
    
    switches = 0
    for i in range(1, len(sessions)):
        prev = sessions[i-1]
        curr = sessions[i]
        
        if prev.started_at.date() == curr.started_at.date():
            gap = (curr.started_at - prev.ended_at).total_seconds()
            if gap < 600 and prev.project != curr.project:
                switches += 1
                
    active_days = len(set(s.started_at.date() for s in sessions))
    avg_per_day = total_sessions / active_days if active_days > 0 else 0
    
    return {
        "avg_session_seconds": int(avg),
        "longest_session_seconds": longest,
        "total_sessions": total_sessions,
        "avg_sessions_per_day": round(avg_per_day, 1),
        "context_switches": switches
    }

@router.get("/summary/latest")
async def get_latest_summary(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Summary).order_by(Summary.generated_at.desc()).limit(1))
    summary = res.scalars().first()
    if not summary:
        return {"content": "No summary available yet.", "generated_at": None}
    return {"content": summary.content, "generated_at": summary.generated_at.isoformat()}

from app.services.ai_summary import generate_weekly_summary

@router.post("/summary/generate")
async def generate_summary_endpoint(db: AsyncSession = Depends(get_db)):
    content = await generate_weekly_summary(db)
    return {"status": "success", "content": content}

