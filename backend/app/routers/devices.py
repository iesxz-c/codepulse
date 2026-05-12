import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceOut, DeviceCreated
from app.middleware.auth import hash_api_key

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("", response_model=DeviceCreated)
async def create_device(device_in: DeviceCreate, db: AsyncSession = Depends(get_db)):
    raw_key = "cp_" + secrets.token_hex(16)
    key_hash = hash_api_key(raw_key)
    prefix = raw_key[:7]
    
    device = Device(
        name=device_in.name,
        api_key_hash=key_hash,
        api_key_prefix=prefix
    )
    db.add(device)
    try:
        await db.commit()
        await db.refresh(device)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
        
    return DeviceCreated(
        id=device.id,
        name=device.name,
        api_key_prefix=device.api_key_prefix,
        created_at=device.created_at,
        api_key=raw_key
    )

@router.get("", response_model=list[DeviceOut])
async def list_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).order_by(Device.created_at.desc()))
    return result.scalars().all()

@router.delete("/{device_id}")
async def delete_device(device_id: str, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await db.delete(device)
    await db.commit()
    return {"status": "deleted"}
