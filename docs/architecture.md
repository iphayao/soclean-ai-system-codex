# Architecture

The SoClean Agentic AI Content System is a monorepo MVP for generating, reviewing, approving, exporting, and measuring Thai marketing content for SoClean tissue products.

## Components

- `apps/web`: Next.js, React, and TypeScript admin UI.
- `apps/api`: FastAPI backend with SQLAlchemy models, routers, LangGraph workflow code, Celery tasks, and deterministic reviewer rules.
- `infra/postgres/init.sql`: PostgreSQL schema, pgvector extension, indexes, and SoClean seed data.
- `prompts`: Prompt templates loaded by agent name for the OpenAI-compatible LLM service.
- `docs`: Architecture, API, workflow, and setup documentation.
- `examples/performance-import.csv`: Sample analytics CSV import file.

## Runtime Services

Docker Compose starts:

- `postgres`: PostgreSQL 16 with pgvector.
- `redis`: Broker and result backend for Celery.
- `api`: FastAPI application on port `8000`.
- `worker`: Celery worker that runs content generation jobs.
- `web`: Next.js app on port `3000`.

## Data Flow

1. A user creates or edits brand memory, products, and campaigns in the web app.
2. The campaign detail page calls `POST /api/campaigns/{campaign_id}/generate-content`.
3. The API creates a `generation_jobs` row and enqueues a Celery task.
4. The worker runs the LangGraph content factory.
5. The graph stores generated `content_items`, `agent_runs`, `agent_run_steps`, `prompt_versions`, and `llm_usage_logs`.
6. A human reviews content in the dashboard and creates an approval record.
7. Approved content with an approved human approval record can be exported to n8n.
8. Performance CSV rows are imported into `content_analytics_metrics`.

## Safety Boundaries

The deterministic reviewer rule engine runs before any LLM reviewer result can pass. It blocks risky SoClean claims including:

- `ไร้ฝุ่น 100%`
- `ไม่ก่อภูมิแพ้`
- `ฆ่าเชื้อโรค`
- `ปลอดภัยที่สุด`
- `medical grade`
- `antibacterial`
- `hypoallergenic`

Generated content is saved as `in_review` only when review passes. It still requires human approval before export.

## Human Approval Before Export

The export endpoint requires both:

- `content_items.status = approved`
- at least one `approvals` row for that content item with `status = approved`

This prevents direct status edits from bypassing review.
