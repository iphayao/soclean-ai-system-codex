import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_brand_crud() -> None:
    reset_db()

    created = client.post(
        "/api/brands",
        json={
            "name": "SoClean",
            "slug": "soclean",
            "description": "Cleaning systems",
            "voice": "Practical and confident",
            "compliance_notes": "Avoid unsupported health claims",
        },
    )
    assert created.status_code == 201
    brand = created.json()
    assert brand["name"] == "SoClean"

    listed = client.get("/api/brands")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.patch(f"/api/brands/{brand['id']}", json={"voice": "Clear and useful"})
    assert updated.status_code == 200
    assert updated.json()["voice"] == "Clear and useful"

    deleted = client.delete(f"/api/brands/{brand['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/api/brands/{brand['id']}").status_code == 404


def test_content_workflow_crud() -> None:
    reset_db()

    brand = client.post(
        "/api/brands",
        json={"name": "SoClean", "slug": "soclean"},
    ).json()
    product = client.post(
        "/api/products",
        json={
            "brand_id": brand["id"],
            "name": "SoClean 3",
            "slug": "soclean-3",
            "category": "CPAP maintenance",
            "key_benefits": ["Automated routine"],
        },
    ).json()
    campaign = client.post(
        "/api/campaigns",
        json={
            "brand_id": brand["id"],
            "name": "Routine Confidence",
            "objective": "Educate customers about easier daily upkeep.",
        },
    ).json()

    content = client.post(
        "/api/content-items",
        json={
            "campaign_id": campaign["id"],
            "product_id": product["id"],
            "title": "A Simpler Daily Habit",
            "channel": "social",
            "format": "linkedin_post",
            "status": "in_review",
            "metadata": {"tone": "educational"},
        },
    )
    assert content.status_code == 201
    content_item = content.json()
    assert content_item["metadata"]["tone"] == "educational"

    approval = client.post(
        "/api/approvals",
        json={
            "content_item_id": content_item["id"],
            "reviewer_name": "Brand Review",
            "status": "pending",
        },
    )
    assert approval.status_code == 201
    approval_id = approval.json()["id"]

    approved = client.patch(
        f"/api/approvals/{approval_id}",
        json={"status": "approved", "feedback": "Ready for scheduling."},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
