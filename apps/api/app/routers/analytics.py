import csv
from collections import defaultdict
from datetime import date
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter()

REQUIRED_COLUMNS = {
    "content_id",
    "platform",
    "views",
    "likes",
    "comments",
    "shares",
    "clicks",
    "add_to_cart",
    "orders",
    "revenue",
    "spend",
    "metric_date",
}


def _int_value(row: dict[str, str], key: str) -> int:
    value = row.get(key, "").strip()
    return int(value or 0)


def _float_value(row: dict[str, str], key: str) -> float:
    value = row.get(key, "").strip()
    return float(value or 0)


@router.post("/import-csv", response_model=schemas.AnalyticsImportResponse)
async def import_analytics_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(StringIO(raw))
    if not reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV header is required")

    missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(sorted(missing))}",
        )

    imported = 0
    for row in reader:
        content = db.get(models.ContentItem, row["content_id"])
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown content_id: {row['content_id']}",
            )

        spend = _float_value(row, "spend")
        revenue = _float_value(row, "revenue")
        metric = models.ContentAnalyticsMetric(
            content_id=content.id,
            campaign_id=content.campaign_id,
            platform=row["platform"],
            views=_int_value(row, "views"),
            likes=_int_value(row, "likes"),
            comments=_int_value(row, "comments"),
            shares=_int_value(row, "shares"),
            clicks=_int_value(row, "clicks"),
            add_to_cart=_int_value(row, "add_to_cart"),
            orders=_int_value(row, "orders"),
            revenue=revenue,
            spend=spend,
            roas=revenue / spend if spend > 0 else None,
            metric_date=date.fromisoformat(row["metric_date"]),
            raw_row=dict(row),
        )
        db.add(metric)
        imported += 1

    db.commit()
    return schemas.AnalyticsImportResponse(imported=imported)


@router.get("/campaigns/{campaign_id}", response_model=list[schemas.CampaignAnalyticsRead])
def get_campaign_analytics(campaign_id: str, db: Session = Depends(get_db)):
    metrics = list(
        db.scalars(
            select(models.ContentAnalyticsMetric).where(models.ContentAnalyticsMetric.campaign_id == campaign_id)
        ).all()
    )

    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "clicks": 0,
            "add_to_cart": 0,
            "orders": 0,
            "revenue": 0.0,
            "spend": 0.0,
        }
    )
    for metric in metrics:
        bucket = totals[metric.platform]
        for field in ("views", "likes", "comments", "shares", "clicks", "add_to_cart", "orders"):
            bucket[field] += getattr(metric, field)
        bucket["revenue"] += metric.revenue
        bucket["spend"] += metric.spend

    return [
        schemas.CampaignAnalyticsRead(
            campaign_id=campaign_id,
            platform=platform,
            roas=values["revenue"] / values["spend"] if values["spend"] > 0 else None,
            **values,
        )
        for platform, values in sorted(totals.items())
    ]
