# PriceYard Backend

FastAPI backend for the PriceYard MVP.

## Requirements
- Python 3.11+
- PostgreSQL

## Setup

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `DATABASE_URL` to a PostgreSQL connection string.

Example format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

## Run migrations

```bash
python -m alembic upgrade head
```

## Verify database connection

```bash
python -c "from app.database import verify_database_connection; verify_database_connection(); print('database connection: PASS')"
```

## Run API

```bash
python -m uvicorn app.main:app --reload
```

Health endpoint:

```text
GET /health
```

Expected response:

```json
{"status":"healthy"}
```
