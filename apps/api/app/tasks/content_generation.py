from app import models, schemas
from app.agents.content_factory import run_content_factory
from app.celery_app import celery_app
from app.database import SessionLocal, init_db


@celery_app.task(name="app.tasks.content_generation.generate_campaign_content")
def generate_campaign_content_task(job_id: str, campaign_id: str, request_data: dict) -> dict:
    init_db()
    db = SessionLocal()
    try:
        job = db.get(models.GenerationJob, job_id)
        if job is None:
            raise ValueError(f"Generation job not found: {job_id}")

        job.status = "running"
        db.commit()

        request = schemas.GenerateContentRequest(**request_data)
        result = run_content_factory(db=db, campaign_id=campaign_id, request=request)

        job.status = "completed"
        job.result_metadata = {
            "agent_run_id": result.agent_run_id,
            "review_passed": result.review_passed,
            "retry_count": result.retry_count,
            "content_item_ids": result.content_item_ids,
        }
        db.commit()
        return {"job_id": job.id, "status": job.status, **job.result_metadata}
    except Exception as exc:
        if "job" in locals() and job is not None:
            job.status = "failed"
            job.error = str(exc)
            db.commit()
        raise
    finally:
        db.close()
