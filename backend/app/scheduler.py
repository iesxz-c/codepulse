from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import AsyncSessionLocal
from app.services.ai_summary import generate_weekly_summary
from app.services.digest import send_digest_email
from app.services.session_engine import process_recent
from app.models.device import Device
from sqlalchemy import select
import logging

scheduler = AsyncIOScheduler()

async def run_weekly_summary():
    async with AsyncSessionLocal() as db:
        content = await generate_weekly_summary(db)
        await send_digest_email(content)
        
async def process_all_devices():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Device))
        devices = res.scalars().all()
        for d in devices:
            try:
                await process_recent(str(d.id), db)
            except Exception as e:
                logging.error(f"Error processing device {d.id}: {e}")

def start_scheduler():
    scheduler.add_job(run_weekly_summary, 'cron', day_of_week='mon', hour=9)
    scheduler.add_job(process_all_devices, 'interval', hours=1)
    
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
