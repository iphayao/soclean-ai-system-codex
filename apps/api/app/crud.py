from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


def list_records(db: Session, model: type[ModelT]) -> list[ModelT]:
    return list(db.scalars(select(model)).all())


def get_record(db: Session, model: type[ModelT], record_id: str) -> ModelT:
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return record


def create_record(db: Session, model: type[ModelT], data: dict[str, Any]) -> ModelT:
    record = model(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, model: type[ModelT], record_id: str, data: dict[str, Any]) -> ModelT:
    record = get_record(db, model, record_id)
    for key, value in data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, model: type[ModelT], record_id: str) -> None:
    record = get_record(db, model, record_id)
    db.delete(record)
    db.commit()
