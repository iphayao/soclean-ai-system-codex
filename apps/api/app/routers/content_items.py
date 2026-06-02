from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter()


@router.get("", response_model=list[schemas.ContentItemRead])
def list_content_items(db: Session = Depends(get_db)):
    return crud.list_records(db, models.ContentItem)


@router.post("", response_model=schemas.ContentItemRead, status_code=status.HTTP_201_CREATED)
def create_content_item(payload: schemas.ContentItemCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["item_metadata"] = data.pop("metadata")
    return crud.create_record(db, models.ContentItem, data)


@router.get("/{content_item_id}", response_model=schemas.ContentItemRead)
def get_content_item(content_item_id: str, db: Session = Depends(get_db)):
    return crud.get_record(db, models.ContentItem, content_item_id)


@router.patch("/{content_item_id}", response_model=schemas.ContentItemRead)
def update_content_item(content_item_id: str, payload: schemas.ContentItemUpdate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    if "metadata" in data:
        data["item_metadata"] = data.pop("metadata")
    return crud.update_record(db, models.ContentItem, content_item_id, data)


@router.delete("/{content_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content_item(content_item_id: str, db: Session = Depends(get_db)):
    crud.delete_record(db, models.ContentItem, content_item_id)
