from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AlertCreate(BaseModel):
    host_id: str
    service_name: Optional[str] = None
    metric_name: str
    metric_value: float
    threshold_value: Optional[float] = None
    severity: str = "CRITICAL"
    rule_id: str
    message: str

class AlertOut(AlertCreate):
    id: int
    timestamp: datetime
    incident_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class IncidentCreate(BaseModel):
    title: str
    service_name: str
    severity: str = "HIGH"

class IncidentOut(BaseModel):
    id: int
    title: str
    service_name: str
    severity: str
    status: str
    created_at: datetime
    suspected_root_cause: Optional[str] = None
    confidence_score: float
    summary_markdown: Optional[str] = None
    alerts: List[AlertOut] = []

    class Config:
        from_attributes = True

class NodeCreate(BaseModel):
    id: str
    name: str
    node_type: str
    environment: str = "production"
    meta_info: Optional[Dict[str, Any]] = None

class EdgeCreate(BaseModel):
    source_id: str
    target_id: str
    relation: str = "DEPENDS_ON"

class RCARequest(BaseModel):
    incident_id: int
    symptom_node_id: str

class RCAResponse(BaseModel):
    incident_id: int
    suspected_root_cause: str
    confidence_score: float
    causal_path: List[str]
    symptoms: List[str]
    post_mortem_summary: str
