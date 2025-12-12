from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket import manager

router = APIRouter()

@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    # In a real app, we should validate the user via token here.
    # For MVP/Desktop, we might assume client_id IS the user_id or a trusted token.
    # Let's treat client_id as user_id for now.
    await manager.connect(websocket, user_id=client_id)
    try:
        while True:
            # Just keep connection alive, maybe listen for pings
            data = await websocket.receive_text()
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=client_id)
