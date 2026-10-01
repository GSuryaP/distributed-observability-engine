import psutil
import time
import socket
from datetime import datetime, timezone

def collect_host_metrics():
    """Collects CPU, Memory, Disk, and Network telemetry from the host."""
    host_id = socket.gethostname()
    
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_times_pct = psutil.cpu_times_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "metrics": {
            "cpu_utilization_percent": cpu_percent,
            "cpu_user_percent": getattr(cpu_times_pct, 'user', 0.0),
            "cpu_system_percent": getattr(cpu_times_pct, 'system', 0.0),
            "cpu_iowait_percent": getattr(cpu_times_pct, 'iowait', 0.0),
            "memory_total_bytes": mem.total,
            "memory_used_percent": mem.percent,
            "disk_used_percent": disk.percent,
            "net_bytes_sent": net_io.bytes_sent,
            "net_bytes_recv": net_io.bytes_recv,
            "net_drop_in": net_io.dropin,
            "net_drop_out": net_io.dropout
        }
    }

if __name__ == "__main__":
    import json
    print(json.dumps(collect_host_metrics(), indent=2))
