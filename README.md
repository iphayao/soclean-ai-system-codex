# SoClean Agentic AI Content System

An MVP admin system for generating, reviewing, approving, exporting, and measuring Thai marketing content for SoClean tissue products.

## Implemented Features

- Monorepo with `apps/web` and `apps/api`
- Next.js, React, and TypeScript admin dashboard
- FastAPI backend with CRUD APIs for brands, products, campaigns, content items, and approvals
- PostgreSQL with pgvector and SoClean seed data
- Redis and Celery for async content generation jobs
- LangGraph content factory workflow
- OpenAI-compatible LLM abstraction with deterministic mock fallback
- Prompt files in `prompts`
- LLM usage logging and prompt version tracking
- Deterministic SoClean claim reviewer rule engine
- Human approval workflow before export
- n8n export for approved content
- Analytics CSV import with ROAS calculation
- Campaign analytics table in the performance page
- Backend tests and frontend type checking

## Run Locally

```bash
docker compose up --build
```

Open:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

The first PostgreSQL boot runs `infra/postgres/init.sql`, which creates the schema, enables pgvector, and seeds SoClean brand, product, campaign, content, approval, and brand memory data.

## Environment

Example env files:

- `apps/api/.env.example`
- `apps/web/.env.example`

Optional live LLM mode:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"
docker compose up --build
```

If `OPENAI_API_KEY` is empty, deterministic mock generation is used.

Optional n8n export mode:

```bash
export N8N_WEBHOOK_URL="https://your-n8n.example/webhook/..."
export N8N_WEBHOOK_SECRET="..."
docker compose up --build
```

## Run Tests

Backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Frontend:

```bash
npm install
npm --workspace apps/web run typecheck
```

Docker Compose validation:

```bash
docker compose config
```

## Core Workflows

Content generation:

1. Create or select a campaign.
2. Click generate content.
3. The API enqueues a Celery job.
4. The worker runs the LangGraph workflow.
5. Generated content is saved as `in_review` when automated review passes.

Review and export:

1. Review generated content in the dashboard.
2. Approve or reject the content.
3. Export is allowed only when content status is `approved` and an approved human approval record exists.
4. Successful n8n export updates content status to `exported`.

Analytics:

1. Upload CSV on `/performance`.
2. Required columns are:

```text
content_id,platform,views,likes,comments,shares,clicks,add_to_cart,orders,revenue,spend,metric_date
```

3. ROAS is calculated as `revenue / spend` when spend is greater than zero.

Sample CSV:

```bash
examples/performance-import.csv
```

## SoClean Claim Safety

The deterministic reviewer blocks risky product claims before an LLM reviewer result can pass.

Banned claims:

- `ไร้ฝุ่น 100%`
- `ไม่ก่อภูมิแพ้`
- `ฆ่าเชื้อโรค`
- `ปลอดภัยที่สุด`
- `medical grade`
- `antibacterial`
- `hypoallergenic`

Preferred safer claims:

- `เนียนนุ่ม`
- `สะอาด`
- `ฝุ่นน้อย`
- `ไม่ฟุ้งง่าย`

Product facts used by default:

- `2 ชั้น`
- `180 แผ่น`
- `5 ห่อต่อแพ็ก`
- `50 แพ็กต่อกล่อง`

## Documentation

- `docs/architecture.md`
- `docs/api.md`
- `docs/agent-workflows.md`
- `docs/setup.md`

## Screenshots

Screenshots can be added here as the MVP UI stabilizes:

- Dashboard overview
- Brand memory form
- Campaign detail and generation status
- Content review table
- Content detail approval/export actions
- Performance CSV import and analytics table
- Agent run logs

## Troubleshooting

If seed data is stale after schema or seed changes:

```bash
docker compose down -v
docker compose up --build
```

If generation jobs stay queued, confirm Redis and the Celery worker are running:

```bash
docker compose ps
```

If the web app cannot reach the API, confirm:

- API is running at `http://localhost:8000`
- `NEXT_PUBLIC_API_BASE_URL` points to `http://localhost:8000`
- CORS includes `http://localhost:3000`

If n8n export fails, confirm:

- content status is `approved`
- an `approvals` row exists for that content item with `status = approved`
- `N8N_WEBHOOK_URL` is configured
- n8n accepts the `X-N8N-Webhook-Secret` header

If live LLM mode fails, unset `OPENAI_API_KEY` to return to deterministic mock mode.

## Next Recommended Improvements

- Add database migrations with Alembic instead of relying only on init SQL.
- Add authentication and role-based permissions for reviewers and admins.
- Add persistent brand memory embeddings and retrieval-backed prompt context.
- Add richer approval history and immutable audit events.
- Add n8n workflow templates and delivery-channel specific payload mappings.
- Add campaign filtering, pagination, and search.
- Add visual regression screenshots for the frontend.
- Add production deployment manifests and secret management.
