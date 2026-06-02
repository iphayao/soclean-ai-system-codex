# SoClean Agentic AI Content System

Phase 1 through Phase 3 skeleton for the SoClean Agentic AI Content System.

## Stack

- Monorepo
- `apps/web`: Next.js, React, TypeScript
- `apps/api`: Python FastAPI
- PostgreSQL with pgvector
- Redis
- Docker Compose

Phase 3 adds a LangGraph content factory workflow with deterministic mocked outputs. Real LLM calls and n8n remain intentionally unimplemented.

## Run Locally

```bash
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

The Phase 3 workflow generates Thai content by default for TikTok, Facebook, and LINE, logs `agent_runs` and `agent_run_steps`, and saves generated `content_items`.

Health check:

- `/health`

## Frontend Pages

- `/` dashboard
- `/brand-memory`
- `/products`
- `/campaigns`
- `/content-review`
