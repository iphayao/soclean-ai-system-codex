from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine
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


def create_generation_fixture() -> tuple[dict, dict, dict]:
    brand = client.post(
        "/api/brands",
        json={
            "name": "SoClean",
            "slug": "soclean",
            "description": "Thai household paper products",
            "voice": "ชัดเจน อบอุ่น และน่าเชื่อถือ",
            "compliance_notes": "Avoid absolute dust, allergy, disinfection, and safest claims.",
        },
    ).json()
    product = client.post(
        "/api/products",
        json={
            "brand_id": brand["id"],
            "name": "SoClean Tissue",
            "slug": "soclean-tissue",
            "category": "Household tissue",
            "description": "2-ply tissue, 180 sheets, 5 packs per bundle, 50 packs per carton.",
            "key_benefits": ["เนียนนุ่ม", "สะอาด", "ฝุ่นน้อย", "ไม่ฟุ้งง่าย"],
        },
    ).json()
    campaign = client.post(
        "/api/campaigns",
        json={
            "brand_id": brand["id"],
            "name": "Thai Social Launch",
            "objective": "Generate Thai content for TikTok, Facebook, and LINE.",
        },
    ).json()
    return brand, product, campaign


def test_generate_content_endpoint_creates_content_items() -> None:
    reset_db()
    _, _, campaign = create_generation_fixture()

    response = client.post(f"/api/campaigns/{campaign['id']}/generate-content", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["campaign_id"] == campaign["id"]
    assert payload["job_id"]

    job_response = client.get(f"/api/jobs/{payload['job_id']}")
    assert job_response.status_code == 200
    job = job_response.json()
    assert job["status"] == "completed"
    assert job["result_metadata"]["review_passed"] is True
    assert job["result_metadata"]["retry_count"] == 0
    assert len(job["result_metadata"]["content_item_ids"]) == 3

    listed = client.get("/api/content-items")
    assert listed.status_code == 200
    assert len(listed.json()) == 3
    assert {item["channel"] for item in listed.json()} == {"TikTok", "Facebook", "LINE"}
    assert all("2 ชั้น" in item["body"] for item in listed.json())

    with SessionLocal() as db:
        generation_jobs = list(db.scalars(select(models.GenerationJob)).all())
        assert len(generation_jobs) == 1
        assert generation_jobs[0].status == "completed"
        agent_runs = list(db.scalars(select(models.AgentRun)).all())
        assert len(agent_runs) == 1
        assert agent_runs[0].status == "completed"
        prompt_versions = list(db.scalars(select(models.PromptVersion)).all())
        assert {version.agent_name for version in prompt_versions} == {
            "campaign_planner",
            "copywriter",
            "visual_brief",
            "reviewer",
        }
        usage_logs = list(db.scalars(select(models.LLMUsageLog)).all())
        assert len(usage_logs) == 4
        assert {log.agent_name for log in usage_logs} == {
            "campaign_planner",
            "copywriter",
            "visual_brief",
            "reviewer",
        }
        assert all(log.model_name == "deterministic-mock" for log in usage_logs)
        steps = list(db.scalars(select(models.AgentRunStep).order_by(models.AgentRunStep.step_order)).all())
        assert [step.step_name for step in steps] == [
            "load_brand_memory",
            "generate_customer_insights",
            "generate_content_strategy",
            "generate_campaign_plan",
            "generate_content",
            "generate_visual_briefs",
            "review_content",
            "save_content",
        ]
