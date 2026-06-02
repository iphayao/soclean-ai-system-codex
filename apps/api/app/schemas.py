from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BrandBase(APIModel):
    name: str
    slug: str
    description: str | None = None
    voice: str | None = None
    compliance_notes: str | None = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(APIModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    voice: str | None = None
    compliance_notes: str | None = None


class BrandRead(BrandBase):
    id: str
    created_at: datetime
    updated_at: datetime


class ProductBase(APIModel):
    brand_id: str
    name: str
    slug: str
    category: str
    description: str | None = None
    key_benefits: list[str] = Field(default_factory=list)
    price_cents: int | None = None
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(APIModel):
    brand_id: str | None = None
    name: str | None = None
    slug: str | None = None
    category: str | None = None
    description: str | None = None
    key_benefits: list[str] | None = None
    price_cents: int | None = None
    active: bool | None = None


class ProductRead(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime


class CampaignBase(APIModel):
    brand_id: str
    name: str
    objective: str
    status: str = "draft"
    start_date: date | None = None
    end_date: date | None = None
    target_audience: str | None = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(APIModel):
    brand_id: str | None = None
    name: str | None = None
    objective: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    target_audience: str | None = None


class CampaignRead(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime


class ContentItemBase(APIModel):
    campaign_id: str
    product_id: str | None = None
    title: str
    channel: str
    format: str
    status: str = "draft"
    body: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContentItemCreate(ContentItemBase):
    pass


class ContentItemUpdate(APIModel):
    campaign_id: str | None = None
    product_id: str | None = None
    title: str | None = None
    channel: str | None = None
    format: str | None = None
    status: str | None = None
    body: str | None = None
    metadata: dict[str, Any] | None = None


class ContentItemRead(ContentItemBase):
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="item_metadata")
    id: str
    created_at: datetime
    updated_at: datetime


class ApprovalBase(APIModel):
    content_item_id: str
    reviewer_name: str
    status: str = "pending"
    feedback: str | None = None
    decided_at: datetime | None = None


class ApprovalCreate(ApprovalBase):
    pass


class ApprovalUpdate(APIModel):
    content_item_id: str | None = None
    reviewer_name: str | None = None
    status: str | None = None
    feedback: str | None = None
    decided_at: datetime | None = None


class ApprovalRead(ApprovalBase):
    id: str
    created_at: datetime
    updated_at: datetime


class GenerateContentRequest(APIModel):
    language: str = "th"
    platforms: list[str] = Field(default_factory=lambda: ["TikTok", "Facebook", "LINE"])
    max_retries: int = 2
    force_initial_review_failure: bool = False


class AgentRunStepRead(APIModel):
    id: str
    step_order: int
    step_name: str
    status: str
    output_metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


class AgentRunRead(APIModel):
    id: str
    campaign_id: str
    workflow_name: str
    status: str
    retry_count: int
    run_metadata: dict[str, Any] = Field(default_factory=dict)
    output_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    steps: list[AgentRunStepRead] = Field(default_factory=list)


class GenerateContentResponse(APIModel):
    agent_run_id: str
    campaign_id: str
    status: str
    retry_count: int
    review_passed: bool
    content_item_ids: list[str]
    content_items: list[ContentItemRead]
