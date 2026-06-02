# Setup

## Prerequisites

- Docker and Docker Compose
- Node.js 20 or newer for local frontend development
- Python 3.11 or newer for local backend development

## Run With Docker

From the repo root:

```bash
docker compose up --build
```

Open:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Environment Files

Copy examples when running services manually:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Docker Compose reads these values from your shell if exported:

```bash
export OPENAI_API_KEY=""
export OPENAI_MODEL="gpt-4o-mini"
export N8N_WEBHOOK_URL=""
export N8N_WEBHOOK_SECRET=""
```

Leave `OPENAI_API_KEY` empty to use deterministic mock generation.

## Backend Development

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

## Frontend Development

```bash
npm install
npm --workspace apps/web run dev
npm --workspace apps/web run typecheck
```

## Worker Development

Start Redis and Postgres with Docker, then run:

```bash
cd apps/api
source .venv/bin/activate
celery -A app.celery_app.celery_app worker --loglevel=info
```

## Analytics Import

Use the sample CSV:

```bash
curl -X POST http://localhost:8000/api/analytics/import-csv \
  -F "file=@examples/performance-import.csv"
```

If you are using a fresh Docker database, the sample CSV references seeded content ID `content-soclean-line-approved`.

## Troubleshooting

If the database seed data does not look current, remove the Postgres volume and start again:

```bash
docker compose down -v
docker compose up --build
```

If the web app cannot reach the API, check `NEXT_PUBLIC_API_BASE_URL` and make sure the API is available at `http://localhost:8000`.

If content generation stays queued, make sure Redis and the Celery worker are running.

If export fails, confirm:

- the content item status is `approved`
- an approval record exists with `status = approved`
- `N8N_WEBHOOK_URL` is configured
- the n8n webhook accepts the configured `X-N8N-Webhook-Secret` header

If live LLM calls fail, unset `OPENAI_API_KEY` to return to deterministic mock mode.
