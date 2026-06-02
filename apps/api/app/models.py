from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_id() -> str:
    return str(uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
    )


class Brand(Base, TimestampMixin):
    __tablename__ = "brands"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    voice: Mapped[str | None] = mapped_column(Text)
    compliance_notes: Mapped[str | None] = mapped_column(Text)

    products: Mapped[list["Product"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="brand", cascade="all, delete-orphan")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    brand_id: Mapped[str] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    key_benefits: Mapped[list[str]] = mapped_column(JSON, default=list)
    price_cents: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    brand: Mapped[Brand] = relationship(back_populates="products")
    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="product")


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    brand_id: Mapped[str] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    target_audience: Mapped[str | None] = mapped_column(Text)

    brand: Mapped[Brand] = relationship(back_populates="campaigns")
    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class ContentItem(Base, TimestampMixin):
    __tablename__ = "content_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    channel: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    body: Mapped[str | None] = mapped_column(Text)
    item_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="content_items")
    product: Mapped[Product | None] = relationship(back_populates="content_items")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="content_item", cascade="all, delete-orphan")


class Approval(Base, TimestampMixin):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    content_item_id: Mapped[str] = mapped_column(
        ForeignKey("content_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    feedback: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    content_item: Mapped[ContentItem] = relationship(back_populates="approvals")


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_name: Mapped[str] = mapped_column(String, nullable=False, default="content_factory")
    status: Mapped[str] = mapped_column(String, nullable=False, default="running")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    run_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    campaign: Mapped[Campaign] = relationship()
    steps: Mapped[list["AgentRunStep"]] = relationship(back_populates="agent_run", cascade="all, delete-orphan")


class AgentRunStep(Base):
    __tablename__ = "agent_run_steps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    agent_run_id: Mapped[str] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="completed")
    input_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=now_utc)

    agent_run: Mapped[AgentRun] = relationship(back_populates="steps")
