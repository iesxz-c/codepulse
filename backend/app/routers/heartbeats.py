from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Union
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.device import Device
from app.models.heartbeat import Heartbeat
from app.schemas.heartbeat import HeartbeatIn
from app.middleware.auth import get_current_device
from app.redis_client import publish_event
from app.services.session_engine import process_recent
import logging

async def safe_process_recent(device_id: str, db: AsyncSession):
    try:
        await process_recent(device_id, db)
    except Exception as e:
        logging.error(f"Error processing session for device {device_id}: {e}")


router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])

@router.post("")
async def receive_heartbeat(
    heartbeats: Union[HeartbeatIn, List[HeartbeatIn]],
    background_tasks: BackgroundTasks,
    device: Device = Depends(get_current_device),
    db: AsyncSession = Depends(get_db)
):
    if not isinstance(heartbeats, list):
        heartbeats = [heartbeats]
        
    if len(heartbeats) > 50:
        heartbeats = heartbeats[:50]
        
    saved = 0
    skipped = 0
    
    heartbeats.sort(key=lambda x: x.time)
    
    for hb in heartbeats:
        thirty_secs_ago = hb.time - timedelta(seconds=30)
        
        existing_res = await db.execute(
            select(Heartbeat)
            .where(
                and_(
                    Heartbeat.device_id == device.id,
                    Heartbeat.file == hb.file,
                    Heartbeat.project == hb.project,
                    Heartbeat.time >= thirty_secs_ago,
                    Heartbeat.time <= hb.time
                )
            )
            .limit(1)
        )
        existing = existing_res.scalars().first()
        
        if existing:
            skipped += 1
            continue
            
        new_hb = Heartbeat(
            device_id=device.id,
            time=hb.time,
            file=hb.file,
            language=hb.language,
            project=hb.project,
            branch=hb.branch,
            is_write=hb.is_write
        )
        db.add(new_hb)
        saved += 1
        
        if hb == heartbeats[-1]:
            await publish_event(f"live:{device.id}", {
                "file": hb.file,
                "project": hb.project,
                "branch": hb.branch,
                "language": hb.language,
                "time": hb.time.isoformat()
            })
            
    if saved > 0:
        await db.commit()
        background_tasks.add_task(safe_process_recent, str(device.id), db)
        
    return {"saved": saved, "skipped": skipped}
