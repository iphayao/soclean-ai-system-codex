from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.services.n8n_service import N8NService, get_n8n_service

router = APIRouter()


@router.post("/{content_id}/export", response_model=schemas.ContentExportResponse)
def export_content(
    content_id: str,
    db: Session = Depends(get_db),
    n8n_service: N8NService = Depends(get_n8n_service),
):
    content = crud.get_record(db, models.ContentItem, content_id)
    if content.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved content can be exported",
        )

    response_metadata = n8n_service.export_content(content)
    content.status = "exported"
    content.item_metadata = {
        **(content.item_metadata or {}),
        "n8n_export": response_metadata,
    }
    db.commit()
    db.refresh(content)
    return schemas.ContentExportResponse(content_id=content.id, status=content.status, exported=True)
