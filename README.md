# SoClean Agentic AI Content System

Phase 1 through Phase 3 skeleton for the SoClean Agentic AI Content System.

## Stack

- Monorepo
- `apps/web`: Next.js, React, TypeScript
- `apps/api`: Python FastAPI
- PostgreSQL with pgvector
- Redis
- Celery worker for async content generation
- Docker Compose

Phase 3 adds a LangGraph content factory workflow with deterministic mocked outputs.
Phase 4 adds an OpenAI-compatible LLM service abstraction. If `OPENAI_API_KEY` is not set, the backend falls back to deterministic mock JSON so local tests and demos remain repeatable.
Phase 8 adds approved-content export to n8n and CSV analytics import for campaign performance reporting.

## Run Locally

```bash
docker compose up --build
```

Optional live LLM mode:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"
docker compose up --build
```

Optional n8n export mode:

```bash
export N8N_WEBHOOK_URL="https://your-n8n.example/webhook/..."
export N8N_WEBHOOK_SECRET="..."
docker compose up --build
```

Then open:

- Web: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

The first PostgreSQL boot runs `infra/postgres/init.sql`, which creates the schema, enables pgvector, and seeds SoClean brand/product/campaign/content data.

## Local Development

Backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Frontend:

```bash
npm install
npm --workspace apps/web run dev
npm --workspace apps/web run typecheck
```

## API Resources

CRUD endpoints are available under:

- `/api/brands`
- `/api/products`
- `/api/campaigns`
- `/api/content-items`
- `/api/approvals`

Agent workflow endpoint:

- `POST /api/campaigns/{campaign_id}/generate-content`
- `GET /api/jobs/{job_id}`

The content generation endpoint enqueues a Celery job and returns a `job_id` immediately. The worker runs the LangGraph workflow, saves generated `content_items`, and logs `agent_runs` / `agent_run_steps`.
Phase 4 prompt files live in `/prompts`, and LLM calls are logged to `llm_usage_logs` with prompt versions in `prompt_versions`.

n8n export and analytics endpoints:

- `POST /api/content/{content_id}/export`
- `POST /api/analytics/import-csv`
- `GET /api/analytics/campaigns/{campaign_id}`

Only approved content can be exported. Analytics CSV imports require `content_id,platform,views,likes,comments,shares,clicks,add_to_cart,orders,revenue,spend,metric_date`; ROAS is calculated as `revenue / spend` when spend is greater than zero.

Health check:

- `/health`

## Frontend Pages

- `/` dashboard
- `/brand-memory`
- `/products`
- `/campaigns`
- `/content-review`
