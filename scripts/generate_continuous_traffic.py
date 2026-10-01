import sys
import os
import time
import math
import random
import requests
import logging

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("graph_generator")

def generate_report_graph_data(host_id: str = "chintu-ubuntu", backend_url: str = "http://localhost:8000"):
    """
    Generates a dense, smooth 4-minute time-series waveform with a baseline,
    a sharp chaos outage spike, and a recovery phase.
    """
    logger.info(f"📊 Generating publication-quality report time-series for host '{host_id}'...")

    total_seconds = 180  # 3 minutes of dense time-series data
    
    for t in range(total_seconds):
        # Determine wave phase
        if t < 50:
            # Phase 1: Healthy Baseline (25-35% CPU, 45% RAM, 0.0 slope)
            cpu = 28.0 + (math.sin(t / 5.0) * 4.0) + random.uniform(-1.5, 1.5)
            ram = 45.0 + random.uniform(-0.5, 0.5)
            slope = random.uniform(-0.02, 0.02)
            iowait = random.uniform(0.1, 0.5)
            net_tx = 1200000.0 + random.uniform(-50000, 50000)
            net_rx = 2500000.0 + random.uniform(-100000, 100000)
            phase = "NORMAL BASELINE"

        elif 50 <= t < 120:
            # Phase 2: CPU Saturation & Latency Spike Chaos Incident (92-98% CPU, +0.85 slope)
            progress = (t - 50) / 10.0
            ramp = min(1.0, progress)
            cpu = 30.0 + (65.0 * ramp) + random.uniform(-1.0, 1.5)
            cpu = min(98.5, cpu)
            ram = 45.0 + (40.0 * ramp) + random.uniform(-1.0, 1.0)
            slope = 0.85 if t < 80 else 0.05
            iowait = 12.5 * ramp
            net_tx = 4500000.0 + random.uniform(-200000, 200000)
            net_rx = 8900000.0 + random.uniform(-400000, 400000)
            phase = "🔥 CHAOS OUTAGE SPIKE"

        else:
            # Phase 3: System Recovery Phase (cooling down to 30%)
            progress = (t - 120) / 15.0
            cool = max(0.0, 1.0 - progress)
            cpu = 30.0 + (62.0 * cool) + random.uniform(-1.5, 1.5)
            ram = 45.0 + (35.0 * cool) + random.uniform(-1.0, 1.0)
            slope = -0.65 if cool > 0 else 0.0
            iowait = 0.5
            net_tx = 1200000.0 + random.uniform(-50000, 50000)
            net_rx = 2500000.0 + random.uniform(-100000, 100000)
            phase = "RECOVERY"

        payload = {
            "host_id": host_id,
            "features": {
                "cpu_mean_5m": round(cpu, 2),
                "cpu_std_5m": round(random.uniform(0.5, 2.5), 2),
                "cpu_slope_1m": round(slope, 3),
                "memory_mean_5m": round(ram, 2),
                "iowait_mean_5m": round(iowait, 2),
                "net_tx_throughput_bytes": round(net_tx, 2),
                "net_rx_throughput_bytes": round(net_rx, 2)
            }
        }

        try:
            requests.post(f"{backend_url}/api/v1/metrics/ingest", json=payload, timeout=1.0)
        except Exception:
            pass

        if t % 15 == 0:
            logger.info(f"[{t}/{total_seconds}s] Phase: {phase} | Host: {host_id} | CPU: {cpu:.1f}% | RAM: {ram:.1f}%")

        time.sleep(0.15)  # Fast generation rate for dense time-series plotting

    logger.info("🎉 Report time-series generation complete! Check Grafana dashboard.")

if __name__ == "__main__":
    host_id = sys.argv[1] if len(sys.argv) > 1 else "chintu-ubuntu"
    generate_report_graph_data(host_id=host_id)
