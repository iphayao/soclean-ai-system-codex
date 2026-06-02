# API

Base URL:

```bash
http://localhost:8000
```

Interactive docs:

```bash
http://localhost:8000/docs
```

## Health

- `GET /health`

## CRUD Resources

- `GET /api/brands`
- `POST /api/brands`
- `GET /api/brands/{brand_id}`
- `PATCH /api/brands/{brand_id}`
- `DELETE /api/brands/{brand_id}`
- `GET /api/products`
- `POST /api/products`
- `GET /api/products/{product_id}`
- `PATCH /api/products/{product_id}`
- `DELETE /api/products/{product_id}`
- `GET /api/campaigns`
- `POST /api/campaigns`
- `GET /api/campaigns/{campaign_id}`
- `PATCH /api/campaigns/{campaign_id}`
- `DELETE /api/campaigns/{campaign_id}`
- `GET /api/content-items`
- `POST /api/content-items`
- `GET /api/content-items/{content_item_id}`
- `PATCH /api/content-items/{content_item_id}`
- `DELETE /api/content-items/{content_item_id}`
- `GET /api/approvals`
- `POST /api/approvals`
- `GET /api/approvals/{approval_id}`
- `PATCH /api/approvals/{approval_id}`
- `DELETE /api/approvals/{approval_id}`

## Content Generation

Enqueue generation:

```bash
curl -X POST http://localhost:8000/api/campaigns/{campaign_id}/generate-content \
  -H "Content-Type: application/json" \
  -d '{"language":"th","platforms":["TikTok","Facebook","LINE"],"max_retries":2}'
```

Response:

```json
{
  "job_id": "...",
  "campaign_id": "...",
  "status": "queued"
}
```

Poll job status:

```bash
curl http://localhost:8000/api/jobs/{job_id}
```

Job statuses:

- `queued`
- `running`
- `completed`
- `failed`

## Agent Runs

- `GET /api/agent-runs`
- `GET /api/agent-runs/{agent_run_id}`

Agent runs include workflow metadata and step logs.

## n8n Export

Export approved content:

```bash
curl -X POST http://localhost:8000/api/content/{content_id}/export
```

Export requirements:

- content status must be `approved`
- content must have an `approvals` row with `status = approved`
- `N8N_WEBHOOK_URL` must be configured

If content is not approved or lacks human approval, the API returns `400`.

## Analytics CSV Import

Import performance metrics:

```bash
curl -X POST http://localhost:8000/api/analytics/import-csv \
  -F "file=@examples/performance-import.csv"
```

Required columns:

```text
content_id,platform,views,likes,comments,shares,clicks,add_to_cart,orders,revenue,spend,metric_date
```

ROAS is calculated as `revenue / spend` when spend is greater than zero.

Campaign analytics:

```bash
curl http://localhost:8000/api/analytics/campaigns/{campaign_id}
```
