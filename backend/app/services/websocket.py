from typing import List, Dict
from fastapi import WebSocket
from collections import defaultdict

import json
import asyncio
from redis import asyncio as aioredis
from app.core.config import settings

class ConnectionManager:
    def __init__(self):
        # Store connections as {user_id: [WebSocket]}
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.redis = None
        self.pubsub = None

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[str(user_id)].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        user_id = str(user_id)
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        user_id = str(user_id)
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

    async def broadcast(self, message: dict):
        # Broadcast to EVERYONE
        for user_sockets in self.active_connections.values():
            for connection in user_sockets:
                try:
                    await connection.send_json(message)
                except:
                    pass

    async def start_redis_listener(self):
        """
        Listen to Redis channel for updates from Celery workers.
        """
        print("WS: Starting Redis Listener...")
        if not settings.CELERY_BROKER_URL:
            print("WS: CELERY_BROKER_URL is missing. Listener aborting.")
            return

        try:
            self.redis = aioredis.from_url(settings.CELERY_BROKER_URL)
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("brain_vault_updates")
            print(f"WS: Subscribed to 'brain_vault_updates' on {settings.CELERY_BROKER_URL}")
            
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        print(f"WS: Received Redis message: {message['data']}")
                        data = json.loads(message["data"])
                        msg_type = data.get("target_type", "broadcast") # broadcast or personal
                        payload = data.get("payload", {})
                        
                        if msg_type == "personal":
                            target_user = data.get("user_id")
                            if target_user:
                                print(f"WS: Sending personal message to {target_user}")
                                await self.send_personal_message(payload, target_user)
                        else:
                            print("WS: Broadcasting message")
                            await self.broadcast(payload)
                    except Exception as e:
                        print(f"Redis Listener Error processing message: {e}")
        except Exception as e:
             print(f"Redis Listener failed to start: {e}")

manager = ConnectionManager()
