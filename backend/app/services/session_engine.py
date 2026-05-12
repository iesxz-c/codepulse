from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.heartbeat import Heartbeat
from app.models.session import Session
import json

async def process_recent(device_id: str, db: AsyncSession):
    now = datetime.now(timezone.utc)
    two_hours_ago = now - timedelta(hours=2)
    
    result = await db.execute(
        select(Heartbeat)
        .where(
            and_(
                Heartbeat.device_id == device_id,
                Heartbeat.time >= two_hours_ago
            )
        )
        .order_by(Heartbeat.time.asc())
    )
    heartbeats = result.scalars().all()
    
    if not heartbeats:
        return
        
    sessions = []
    current_session = []
    
    for i, hb in enumerate(heartbeats):
        if not current_session:
            current_session.append(hb)
            continue
            
        prev_hb = current_session[-1]
        gap = hb.time - prev_hb.time
        
        if gap.total_seconds() > 300: # 5 minutes gap
            sessions.append(current_session)
            current_session = [hb]
        else:
            current_session.append(hb)
            
    if current_session:
        sessions.append(current_session)
        
    for sess_hbs in sessions:
        if not sess_hbs:
            continue
            
        start_time = sess_hbs[0].time
        end_time = sess_hbs[-1].time
        duration = int((end_time - start_time).total_seconds())
        
        if duration <= 60:
            continue
            
        lang_counts = {}
        proj_counts = {}
        branch_counts = {}
        
        for hb in sess_hbs:
            if hb.language:
                lang_counts[hb.language] = lang_counts.get(hb.language, 0) + 30
            if hb.project:
                proj_counts[hb.project] = proj_counts.get(hb.project, 0) + 1
            if hb.branch:
                branch_counts[hb.branch] = branch_counts.get(hb.branch, 0) + 1
                
        dominant_project = max(proj_counts.items(), key=lambda x: x[1])[0] if proj_counts else None
        dominant_branch = max(branch_counts.items(), key=lambda x: x[1])[0] if branch_counts else None
        
        existing_result = await db.execute(
            select(Session)
            .where(
                and_(
                    Session.device_id == device_id,
                    Session.started_at == start_time
                )
            )
        )
        existing = existing_result.scalars().first()
        
        if existing:
            existing.ended_at = end_time
            existing.duration_seconds = duration
            existing.languages = lang_counts
            existing.project = dominant_project
            existing.branch = dominant_branch
        else:
            new_session = Session(
                device_id=device_id,
                project=dominant_project,
                branch=dominant_branch,
                started_at=start_time,
                ended_at=end_time,
                duration_seconds=duration,
                languages=lang_counts
            )
            db.add(new_session)
            
    await db.commit()
