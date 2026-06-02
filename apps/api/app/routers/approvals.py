from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter()


@router.get("", response_model=list[schemas.ApprovalRead])
def list_approvals(db: Session = Depends(get_db)):
    return crud.list_records(db, models.Approval)


@router.post("", response_model=schemas.ApprovalRead, status_code=status.HTTP_201_CREATED)
def create_approval(payload: schemas.ApprovalCreate, db: Session = Depends(get_db)):
    return crud.create_record(db, models.Approval, payload.model_dump())


@router.get("/{approval_id}", response_model=schemas.ApprovalRead)
def get_approval(approval_id: str, db: Session = Depends(get_db)):
    return crud.get_record(db, models.Approval, approval_id)


@router.patch("/{approval_id}", response_model=schemas.ApprovalRead)
def update_approval(approval_id: str, payload: schemas.ApprovalUpdate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    return crud.update_record(db, models.Approval, approval_id, data)


@router.delete("/{approval_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_approval(approval_id: str, db: Session = Depends(get_db)):
    crud.delete_record(db, models.Approval, approval_id)
