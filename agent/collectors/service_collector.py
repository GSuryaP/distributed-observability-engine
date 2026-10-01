import time
import socket
import requests
from datetime import datetime, timezone
import logging

logger = logging.getLogger("service_collector")

def check_tcp_service(host: str, port: int, timeout: float = 1.0) -> dict:
    """Checks TCP connection latency and availability for a service port."""
    start = time.perf_counter()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {"status": "UP", "latency_ms": latency_ms}
    except Exception as e:
        return {"status": "DOWN", "latency_ms": -1.0, "error": str(e)}

def collect_service_metrics(host_id: str = "host-prod-01", redis_host="localhost", redis_port=6379, postgres_host="localhost", postgres_port=5432):
    """Probes status and latency of core services (Redis, Postgres, HTTP API)."""
    redis_check = check_tcp_service(redis_host, redis_port)
    postgres_check = check_tcp_service(postgres_host, postgres_port)
    
    # Check sample HTTP service latency
    http_check = {"status": "DOWN", "latency_ms": -1.0}
    try:
        start = time.perf_counter()
        resp = requests.get("http://localhost:8000/health", timeout=1.0)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        http_check = {
            "status": "UP" if resp.status_code == 200 else "DEGRADED",
            "status_code": resp.status_code,
            "latency_ms": latency_ms
        }
    except Exception:
        pass

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "services": {
            "redis": redis_check,
            "postgresql": postgres_check,
            "http_api": http_check
        }
    }

if __name__ == "__main__":
    import json
    print(json.dumps(collect_service_metrics(), indent=2))
