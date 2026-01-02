from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.db.models import User as ORMUser
from app.services.network_streamer import ConnectionStreamer, clamp_interval_ms


router = APIRouter()
streamer = ConnectionStreamer()


def _authenticate_ws(token: str | None) -> ORMUser | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    db = SessionLocal()
    try:
        user = db.query(ORMUser).filter(ORMUser.username == payload["sub"]).first()
        if not user or not user.is_active:
            return None
        return user
    finally:
        db.close()


@router.websocket("/ws/network")
async def ws_network(
    websocket: WebSocket,
    interval_ms: int = Query(500),
    token: str | None = Query(None),
):
    await websocket.accept()
    user = _authenticate_ws(token)
    if not user:
        await websocket.close(code=1008)
        return

    interval_ms = clamp_interval_ms(interval_ms)
    await streamer.register(websocket, interval_ms)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await streamer.unregister(websocket)
