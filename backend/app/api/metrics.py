from fastapi import APIRouter, status
from typing import Dict, Any, List

from backend.app.engine.rules import rule_engine
from backend.app.engine.ml_anomaly import ml_detector
from backend.app.db.influx import influx_db

router = APIRouter(prefix="/metrics", tags=["Telemetry Metrics"])

@router.post("/ingest", status_code=status.HTTP_200_OK)
def ingest_telemetry_payload(payload: Dict[str, Any]):
    """
    Ingests feature payload, evaluates rule engine + ML anomaly detection,
    and returns detected anomaly scores and alerts.
    """
    host_id = payload.get("host_id", "unknown")
    
    # 1. Rule Engine evaluation
    rule_alerts = rule_engine.evaluate_metrics(payload)
    
    # 2. ML Anomaly detection
    features = payload.get("features", payload.get("metrics", {}))
    anomaly_score, is_anomalous = ml_detector.predict_anomaly(features)
    
    # 3. Time-Series InfluxDB write
    if features:
        influx_db.write_point(
            measurement="host_metrics",
            tags={"host_id": host_id},
            fields={
                "cpu_mean_5m": float(features.get("cpu_mean_5m", 0.0)),
                "memory_mean_5m": float(features.get("memory_mean_5m", 0.0)),
                "anomaly_score": anomaly_score
            }
        )

    return {
        "host_id": host_id,
        "anomaly_score": anomaly_score,
        "status": "ANOMALOUS" if is_anomalous else "HEALTHY",
        "rule_alerts_count": len(rule_alerts),
        "alerts": rule_alerts
    }
