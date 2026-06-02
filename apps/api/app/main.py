import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import agent_runs, analytics, approvals, brands, campaigns, content_export, content_items, jobs, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="SoClean Agentic AI Content System API",
        description="MVP API for SoClean brand memory, campaign content generation, review, export, and analytics.",
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = [origin.strip() for origin in os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
    app.include_router(products.router, prefix="/api/products", tags=["products"])
    app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
    app.include_router(content_items.router, prefix="/api/content-items", tags=["content_items"])
    app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
    app.include_router(agent_runs.router, prefix="/api/agent-runs", tags=["agent_runs"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(content_export.router, prefix="/api/content", tags=["content_export"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

    return app


app = create_app()
