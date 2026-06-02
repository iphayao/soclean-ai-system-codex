from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter()


@router.get("", response_model=list[schemas.ProductRead])
def list_products(db: Session = Depends(get_db)):
    return crud.list_records(db, models.Product)


@router.post("", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_record(db, models.Product, payload.model_dump())


@router.get("/{product_id}", response_model=schemas.ProductRead)
def get_product(product_id: str, db: Session = Depends(get_db)):
    return crud.get_record(db, models.Product, product_id)


@router.patch("/{product_id}", response_model=schemas.ProductRead)
def update_product(product_id: str, payload: schemas.ProductUpdate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    return crud.update_record(db, models.Product, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    crud.delete_record(db, models.Product, product_id)
