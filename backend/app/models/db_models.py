from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    host_id = Column(String, index=True)
    service_name = Column(String, nullable=True, index=True)
    metric_name = Column(String)
    metric_value = Column(Float)
    threshold_value = Column(Float, nullable=True)
    severity = Column(String) # INFO, WARNING, CRITICAL
    rule_id = Column(String)
    message = Column(Text)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)

    incident = relationship("Incident", back_populates="alerts")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    service_name = Column(String, index=True)
    severity = Column(String, default="HIGH") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="OPEN") # OPEN, INVESTIGATING, RESOLVED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    suspected_root_cause = Column(String, nullable=True)
    confidence_score = Column(Float, default=0.0)
    summary_markdown = Column(Text, nullable=True)
    
    alerts = relationship("Alert", back_populates="incident")

class TopologyNode(Base):
    __tablename__ = "topology_nodes"
    
    id = Column(String, primary_key=True) # e.g. "host-01", "service-payment", "db-postgres"
    name = Column(String)
    node_type = Column(String) # HOST, CONTAINER, SERVICE, DATABASE, CACHE
    environment = Column(String, default="production")
    meta_info = Column(JSON, nullable=True)

class TopologyEdge(Base):
    __tablename__ = "topology_edges"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("topology_nodes.id"))
    target_id = Column(String, ForeignKey("topology_nodes.id"))
    relation = Column(String) # DEPENDS_ON, RUNS_ON, CALLS
