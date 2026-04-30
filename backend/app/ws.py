import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

router = APIRouter()

_r = redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True,
)


async def broadcast_view(code: str) -> int:
    count = await _r.incr(f"views:{code}")

    await _r.publish(
        f"chan:{code}",
        json.dumps({"views": count}),
    )

    return count


@router.websocket("/ws/views/{code}")
async def ws_views(ws: WebSocket, code: str):
    await ws.accept()

    current = await _r.get(f"views:{code}") or 0

    await ws.send_text(
        json.dumps({"views": int(current)})
    )

    pubsub = _r.pubsub()
    await pubsub.subscribe(f"chan:{code}")

    try:
        async for msg in pubsub.listen():
            if msg["type"] != "message":
                continue

            await ws.send_text(msg["data"])

    except WebSocketDisconnect:
        pass

    finally:
        await pubsub.unsubscribe(f"chan:{code}")
        await pubsub.close()