import sys
import os
import time
import argparse
import requests
import logging

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chaos.scenarios.cpu_stress import run_cpu_stress
from chaos.scenarios.memory_leak import run_memory_leak

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("chaos_runner")

def trigger_backend_incident_simulation(backend_url: str, scenario_name: str, host_id: str = "host-prod-01"):
    """Posts simulated metric spike to backend to trigger Rule/ML Anomaly alert and RCA creation."""
    logger.info(f"Simulating anomaly event payload to backend at {backend_url}...")
    
    if scenario_name == "cpu_saturation":
        payload = {
            "host_id": host_id,
            "features": {
                "cpu_mean_5m": 96.5,
                "cpu_std_5m": 1.2,
                "cpu_slope_1m": 0.88,
                "memory_mean_5m": 75.0,
                "net_tx_throughput_bytes": 1000000.0,
                "net_rx_throughput_bytes": 2000000.0
            }
        }
    elif scenario_name == "memory_leak":
        payload = {
            "host_id": host_id,
            "features": {
                "cpu_mean_5m": 45.0,
                "cpu_std_5m": 0.5,
                "cpu_slope_1m": 0.05,
                "memory_mean_5m": 94.8,
                "net_tx_throughput_bytes": 500000.0,
                "net_rx_throughput_bytes": 1000000.0
            }
        }
    else:
        payload = {
            "host_id": host_id,
            "features": {
                "cpu_mean_5m": 88.0,
                "memory_mean_5m": 85.0
            }
        }

    try:
        resp = requests.post(f"{backend_url}/api/v1/metrics/ingest", json=payload, timeout=3)
        logger.info(f"Backend Response ({resp.status_code}): {resp.json()}")
        
        # Trigger Incident creation
        inc_payload = {
            "title": f"Chaos Scenario Triggered: {scenario_name}",
            "service_name": "payment-service",
            "severity": "CRITICAL"
        }
        inc_resp = requests.post(f"{backend_url}/api/v1/incidents/", json=inc_payload, timeout=3)
        logger.info(f"Incident Created: {inc_resp.json()}")
    except Exception as e:
        logger.warning(f"Failed to post to backend: {e}")

def main():
    parser = argparse.ArgumentParser(description="Nexus Chaos Injection Engine")
    parser.add_argument("--scenario", choices=["cpu", "memory", "all"], default="cpu", help="Chaos scenario type")
    parser.add_argument("--duration", type=int, default=15, help="Duration in seconds")
    parser.add_argument("--backend-url", type=str, default="http://localhost:8000", help="Backend URL")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting Nexus Chaos Experiment (Scenario: {args.scenario}, Duration: {args.duration}s)")
    
    if args.scenario in ["cpu", "all"]:
        run_cpu_stress(duration_seconds=args.duration)
        trigger_backend_incident_simulation(args.backend_url, "cpu_saturation")
        
    if args.scenario in ["memory", "all"]:
        run_memory_leak(target_mb=400, hold_seconds=args.duration)
        trigger_backend_incident_simulation(args.backend_url, "memory_leak")

    logger.info("🎉 Chaos Experiment completed successfully.")

if __name__ == "__main__":
    main()
