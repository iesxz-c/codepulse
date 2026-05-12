from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.redis_client import get_redis

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/live/{device_id}")
async def live_session(websocket: WebSocket, device_id: str):
    await websocket.accept()
    redis = None
    pubsub = None
    ping_task = None
    
    async def ping():
        while True:
            await asyncio.sleep(30)
            try:
                await websocket.send_json({"type": "ping"})
            except:
                break
                
    try:
        redis_gen = get_redis()
        redis = await anext(redis_gen)
        
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"live:{device_id}")
        
        ping_task = asyncio.create_task(ping())
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
                
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
            except asyncio.TimeoutError:
                pass
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WS error: {e}")
    finally:
        if ping_task:
            ping_task.cancel()
        if pubsub:
            await pubsub.unsubscribe(f"live:{device_id}")
            await pubsub.close()
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close()
