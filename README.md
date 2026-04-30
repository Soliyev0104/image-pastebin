# Image Pastebin

Upload an image, get a short URL back, and watch live view counts over WebSocket.


```
- **nginx** routes `/api/`, `/s/`, `/ws/`, `/images/`, and `/` (frontend).
- **backend** (FastAPI) handles upload, short-code generation, metadata, view page, and WebSocket.
- **image_service** (gRPC, Python + Pillow) compresses, generates a thumbnail, and applies a watermark.
- **postgres** stores the URL table.
- **redis** powers idempotency keys (`X-Request-ID`) and the live view-count pub/sub.

## Running locally

```bash
cp .env.example .env
# edit .env if you want
docker compose up --build
```

## Deploying to a Digital Ocean droplet

```bash
# on the droplet, with Docker installed
git clone <repo-url>
cd image_pastebin
docker compose up --build -d
```

## API

- `POST /api/upload` — multipart form upload (`file`), requires `X-Request-ID` header.
- `GET /api/meta/{code}` — JSON metadata for a short code.
- `GET /s/{code}` — HTML view page with live view counter.
- `GET /docs` — Swagger UI.
- `WS /ws/views/{code}` — view-count stream.

Limits: 10 MB max, MIME must be `image/jpeg`, `image/png`, or `image/webp`.
