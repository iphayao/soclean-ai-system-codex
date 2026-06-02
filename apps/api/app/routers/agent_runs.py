from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("", response_model=list[schemas.AgentRunRead])
def list_agent_runs(db: Session = Depends(get_db)):
    query = select(models.AgentRun).options(selectinload(models.AgentRun.steps)).order_by(models.AgentRun.created_at.desc())
    return list(db.scalars(query).all())
