import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.rate_limiter import limiter
from app.metrics import record_signal, get_metrics, metrics_printer
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT = os.getenv("RATE_LIMIT", "100/second")

# ── Startup: launch background metrics printer ────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(metrics_printer())
    yield

# ── App setup ─────────────────────────────────────────────────────────
app = FastAPI(lifespan=lifespan)

# Attach rate limiter to the app
app.state.limiter = limiter

# When rate limit is exceeded → return 429 with a clear message
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Data model ────────────────────────────────────────────────────────
class Signal(BaseModel):
    component_id: str
    signal_type:  str
    value:        float

# ── Endpoints ─────────────────────────────────────────────────────────

@app.get("/health")
async def health(request: Request):
    """
    Returns server status + live throughput metrics.
    This is your observability endpoint.
    """
    return {
        "status":  "ok",
        "metrics": get_metrics(),
    }

@app.post("/api/signals", status_code=202)
@limiter.limit(RATE_LIMIT)  # ← Rate limit applied here
async def ingest_signal(request: Request, signal: Signal):
    """
    Accepts incoming signals.
    Rate limited — max 100 requests/second per IP.
    If exceeded → returns 429 Too Many Requests automatically.
    """
    record_signal()  # update metrics counter
    return {
        "status":       "accepted",
        "component_id": signal.component_id,
    }

@app.get("/metrics")
async def metrics(request: Request):
    """Detailed metrics endpoint."""
    return get_metrics()