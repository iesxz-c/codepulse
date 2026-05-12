import hashlib
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.device import Device
from app.config import settings

security = HTTPBearer()

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(f"{api_key}{settings.SECRET_KEY}".encode()).hexdigest()

async def get_current_device(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> Device:
    api_key = credentials.credentials
    if not api_key.startswith("cp_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    key_hash = hash_api_key(api_key)
    
    result = await db.execute(select(Device).where(Device.api_key_hash == key_hash))
    device = result.scalars().first()
    
    if not device:
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    return device
