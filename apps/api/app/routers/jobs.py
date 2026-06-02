from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/{job_id}", response_model=schemas.JobRead)
def get_job(job_id: str, db: Session = Depends(get_db)):
    return crud.get_record(db, models.GenerationJob, job_id)
