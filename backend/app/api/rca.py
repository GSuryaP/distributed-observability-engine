from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.postgres import get_db
from backend.app.models.db_models import Incident
from backend.app.models.schemas import RCARequest, RCAResponse
from backend.app.engine.graph_rca import rca_engine
from backend.app.engine.llm_analyst import llm_analyst

router = APIRouter(prefix="/rca", tags=["Root Cause Analysis"])

@router.post("/analyze", response_model=RCAResponse)
def trigger_rca_analysis(payload: RCARequest, db: Session = Depends(get_db)):
    """Executes graph traversal and temporal correlation to identify suspected root cause."""
    incident = db.query(Incident).filter(Incident.id == payload.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    alert_nodes = [a.service_name or a.host_id for a in incident.alerts]
    if payload.symptom_node_id not in alert_nodes:
        alert_nodes.append(payload.symptom_node_id)

    root_cause, confidence, causal_path = rca_engine.analyze_root_cause(
        symptom_node_id=payload.symptom_node_id,
        alert_nodes=alert_nodes
    )

    alerts_dict = [
        {"message": a.message, "severity": a.severity} for a in incident.alerts
    ]

    summary = llm_analyst.generate_incident_report(
        incident_id=incident.id,
        title=incident.title,
        service_name=incident.service_name,
        suspected_root_cause=root_cause,
        confidence_score=confidence,
        causal_path=causal_path,
        alerts=alerts_dict
    )

    # Update incident in DB
    incident.suspected_root_cause = root_cause
    incident.confidence_score = confidence
    incident.summary_markdown = summary
    db.commit()

    return RCAResponse(
        incident_id=incident.id,
        suspected_root_cause=root_cause,
        confidence_score=confidence,
        causal_path=causal_path,
        symptoms=[a.message for a in incident.alerts] or [f"Symptom detected on {payload.symptom_node_id}"],
        post_mortem_summary=summary
    )
