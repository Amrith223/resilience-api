# Resilience API

A high-throughput signal ingestion API built with FastAPI, demonstrating
concurrency, rate limiting, and observability.

## What it does
- Accepts signals via async HTTP POST endpoint
- Rate limits requests to prevent cascading failures
- Exposes a /health endpoint with live throughput metrics
- Prints signals/sec to console every 5 seconds

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI (fully async) |
| Rate Limiting | SlowAPI (per IP, sliding window) |
| Concurrency | Python asyncio |
| Load Testing | httpx (async HTTP client) |

## Key Concepts

### Concurrency
All endpoints use `async/await` — the server never blocks while waiting.
It handles many requests simultaneously without slowing down.

### Rate Limiting
Each client IP is limited to 20 requests/second.
Requests that exceed the limit receive `429 Too Many Requests` instantly.
This protects the system from traffic spikes and cascading failures.

### Observability
Two ways to monitor the system:
- `/health` endpoint — live metrics on demand
- Console printer — throughput stats every 5 seconds automatically

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Server status + live metrics |
| GET | /metrics | Detailed throughput metrics |
| POST | /api/signals | Ingest a signal (rate limited) |

## Sample Responses

### GET /health
```json
