from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter()


@router.get("", response_model=list[schemas.BrandRead])
def list_brands(db: Session = Depends(get_db)):
    return crud.list_records(db, models.Brand)


@router.post("", response_model=schemas.BrandRead, status_code=status.HTTP_201_CREATED)
def create_brand(payload: schemas.BrandCreate, db: Session = Depends(get_db)):
    return crud.create_record(db, models.Brand, payload.model_dump())


@router.get("/{brand_id}", response_model=schemas.BrandRead)
def get_brand(brand_id: str, db: Session = Depends(get_db)):
    return crud.get_record(db, models.Brand, brand_id)


@router.patch("/{brand_id}", response_model=schemas.BrandRead)
def update_brand(brand_id: str, payload: schemas.BrandUpdate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    return crud.update_record(db, models.Brand, brand_id, data)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(brand_id: str, db: Session = Depends(get_db)):
    crud.delete_record(db, models.Brand, brand_id)
