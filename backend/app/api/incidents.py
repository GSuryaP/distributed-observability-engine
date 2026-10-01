from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.postgres import get_db
from backend.app.models.db_models import Incident, Alert
from backend.app.models.schemas import IncidentOut, IncidentCreate, AlertCreate, AlertOut
from backend.app.engine.graph_rca import rca_engine
from backend.app.engine.llm_analyst import llm_analyst

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("/", response_model=List[IncidentOut])
def get_incidents(db: Session = Depends(get_db)):
    """Retrieves all incidents sorted by creation date."""
    return db.query(Incident).order_by(Incident.created_at.desc()).all()

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Retrieves detailed incident metadata including alerts and post-mortem report."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    """Creates a new Incident record and triggers automated RCA calculation."""
    # Perform automated initial RCA
    suspected_rc, confidence, causal_path = rca_engine.analyze_root_cause(
        symptom_node_id=payload.service_name,
        alert_nodes=[payload.service_name]
    )
    
    incident = Incident(
        title=payload.title,
        service_name=payload.service_name,
        severity=payload.severity,
        suspected_root_cause=suspected_rc,
        confidence_score=confidence
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Generate initial post-mortem report summary
    report = llm_analyst.generate_incident_report(
        incident_id=incident.id,
        title=incident.title,
        service_name=incident.service_name,
        suspected_root_cause=suspected_rc,
        confidence_score=confidence,
        causal_path=causal_path,
        alerts=[]
    )
    incident.summary_markdown = report
    db.commit()
    db.refresh(incident)
    
    return incident
