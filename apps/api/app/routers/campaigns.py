from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.agents.content_factory import run_content_factory
from app.database import get_db

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


@router.post("/{campaign_id}/generate-content", response_model=schemas.GenerateContentResponse)
def generate_campaign_content(
    campaign_id: str,
    payload: schemas.GenerateContentRequest | None = None,
    db: Session = Depends(get_db),
):
    crud.get_record(db, models.Campaign, campaign_id)
    request = payload or schemas.GenerateContentRequest()
    return run_content_factory(db=db, campaign_id=campaign_id, request=request)
