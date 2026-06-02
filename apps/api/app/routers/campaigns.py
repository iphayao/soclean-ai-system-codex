from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.tasks.content_generation import generate_campaign_content_task

router = APIRouter()


@router.get("", response_model=list[schemas.CampaignRead])
def list_campaigns(db: Session = Depends(get_db)):
    return crud.list_records(db, models.Campaign)


@router.post("", response_model=schemas.CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: schemas.CampaignCreate, db: Session = Depends(get_db)):
    return crud.create_record(db, models.Campaign, payload.model_dump())


@router.get("/{campaign_id}", response_model=schemas.CampaignRead)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    return crud.get_record(db, models.Campaign, campaign_id)


@router.patch("/{campaign_id}", response_model=schemas.CampaignRead)
def update_campaign(campaign_id: str, payload: schemas.CampaignUpdate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    return crud.update_record(db, models.Campaign, campaign_id, data)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    crud.delete_record(db, models.Campaign, campaign_id)


@router.post("/{campaign_id}/generate-content", response_model=schemas.GenerateContentJobResponse)
def generate_campaign_content(
    campaign_id: str,
    payload: schemas.GenerateContentRequest | None = None,
    db: Session = Depends(get_db),
):
    crud.get_record(db, models.Campaign, campaign_id)
    request = payload or schemas.GenerateContentRequest()
    job = models.GenerationJob(campaign_id=campaign_id, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)

    task = generate_campaign_content_task.apply_async(
        args=[job.id, campaign_id, request.model_dump()],
        task_id=job.id,
    )
    job.celery_task_id = task.id
    db.commit()
    return schemas.GenerateContentJobResponse(job_id=job.id, campaign_id=campaign_id, status="queued")
