from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas
from .. import models
from ..deps import get_db, get_current_user, require_role

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Incident).all()


@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    incident = db.query(models.Incident).filter_by(id=incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=schemas.IncidentOut, status_code=201)
def create_incident(
    incident: schemas.IncidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_incident = models.Incident(**incident.model_dump())
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    incident = db.query(models.Incident).filter_by(id=incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(incident)
    db.commit()
