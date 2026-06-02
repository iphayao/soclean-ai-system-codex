import os
from typing import Any

import httpx

from app import models


class N8NService:
    def __init__(self, webhook_url: str | None = None, webhook_secret: str | None = None) -> None:
        self.webhook_url = webhook_url if webhook_url is not None else os.getenv("N8N_WEBHOOK_URL")
        self.webhook_secret = webhook_secret if webhook_secret is not None else os.getenv("N8N_WEBHOOK_SECRET")

    def export_content(self, content: models.ContentItem) -> dict[str, Any]:
        if not self.webhook_url:
            raise RuntimeError("N8N_WEBHOOK_URL is not configured")

        payload = {
            "content_id": content.id,
            "campaign_id": content.campaign_id,
            "product_id": content.product_id,
            "title": content.title,
            "channel": content.channel,
            "format": content.format,
            "status": content.status,
            "body": content.body,
            "metadata": content.item_metadata,
        }
        headers = {}
        if self.webhook_secret:
            headers["X-N8N-Webhook-Secret"] = self.webhook_secret

        response = httpx.post(self.webhook_url, json=payload, headers=headers, timeout=20.0)
        response.raise_for_status()
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return {"status_code": response.status_code}


def get_n8n_service() -> N8NService:
    return N8NService()
