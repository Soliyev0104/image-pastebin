import asyncio
import functools
import json
import os

from fastapi import HTTPException, Request
import redis.asyncio as redis

_r: redis.Redis | None = None

TTL = 24 * 3600
PENDING_TTL = 60


def _client():
    global _r

    if _r is None:
        _r = redis.from_url(
            os.environ["REDIS_URL"],
            decode_responses=True,
        )

    return _r


def idempotent(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        req: Request = kwargs["request"]
        rid = req.headers.get("X-Request-ID")

        if not rid:
            raise HTTPException(400, "X-Request-ID header is required")

        key = f"idem:{rid}"
        r = _client()

        ok = await r.set(key, "PENDING", nx=True, ex=PENDING_TTL)

        if not ok:
            for _ in range(30):
                val = await r.get(key)

                if val and val != "PENDING":
                    return json.loads(val)

                await asyncio.sleep(0.1)

            raise HTTPException(409, "Request still in progress")

        try:
            result = await fn(*args, **kwargs)
        except Exception:
            await r.delete(key)
            raise

        await r.set(key, json.dumps(result), ex=TTL)

        return result

    return wrapper