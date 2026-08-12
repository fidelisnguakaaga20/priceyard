# PriceYard Backend

FastAPI backend for PriceYard.

## Stage 2 scope

This stage contains only the backend foundation:

- FastAPI application
- environment-based configuration
- dependency list
- health-check endpoint

Database, authentication, business APIs, and other later-stage features are intentionally not implemented yet.

## Setup

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
```

Optionally copy `.env.example` to `.env` and adjust non-secret local settings.

## Run

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Health check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"healthy"}
```
