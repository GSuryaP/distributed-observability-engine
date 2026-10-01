from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("rule_engine")

class RuleEngine:
    def __init__(self):
        self.rules = [
            {
                "id": "RULE_CPU_SATURATION",
                "metric": "cpu_utilization_percent",
                "condition": ">=",
                "threshold": 90.0,
                "severity": "CRITICAL",
                "message": "Host CPU utilization critical (>= 90%)"
            },
            {
                "id": "RULE_CPU_RAPID_SPIKE",
                "metric": "cpu_slope_1m",
                "condition": ">=",
                "threshold": 0.75,
                "severity": "WARNING",
                "message": "Host CPU metric rising rapidly (slope >= 0.75)"
            },
            {
                "id": "RULE_MEMORY_HIGH",
                "metric": "memory_used_percent",
                "condition": ">=",
                "threshold": 90.0,
                "severity": "CRITICAL",
                "message": "Host memory usage critical (>= 90%)"
            },
            {
                "id": "RULE_HTTP_HIGH_LATENCY",
                "metric": "latency_ms",
                "condition": ">=",
                "threshold": 2000.0,
                "severity": "WARNING",
                "message": "HTTP API response latency high (>= 2000ms)"
            }
        ]

    def evaluate_metrics(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluates input telemetry payload against standard rule set."""
        triggered_alerts = []
        host_id = payload.get("host_id", "unknown")
        service_name = payload.get("service_name", None)
        
        # Flatten metrics dictionary if nested inside features or metrics
        metrics = payload.get("features", payload.get("metrics", {}))
        
        for rule in self.rules:
            metric_val = metrics.get(rule["metric"])
            if metric_val is None:
                continue
                
            is_triggered = False
            if rule["condition"] == ">=" and metric_val >= rule["threshold"]:
                is_triggered = True
            elif rule["condition"] == "<=" and metric_val <= rule["threshold"]:
                is_triggered = True
                
            if is_triggered:
                triggered_alerts.append({
                    "rule_id": rule["id"],
                    "host_id": host_id,
                    "service_name": service_name,
                    "metric_name": rule["metric"],
                    "metric_value": metric_val,
                    "threshold_value": rule["threshold"],
                    "severity": rule["severity"],
                    "message": f"{rule['message']} - Current: {metric_val}"
                })
                
        return triggered_alerts

rule_engine = RuleEngine()
