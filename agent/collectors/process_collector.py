import psutil
from datetime import datetime, timezone

def collect_process_metrics(limit: int = 10, host_id: str = "host-prod-01"):
    """Collects process-level metrics for top N resource consumers."""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'status', 'num_threads', 'cpu_percent', 'memory_percent', 'memory_info']):
        try:
            info = proc.info
            # Filter out low footprint system idle processes if desired
            processes.append({
                "pid": info['pid'],
                "name": info['name'],
                "status": info['status'],
                "num_threads": info['num_threads'],
                "cpu_percent": info['cpu_percent'] or 0.0,
                "memory_percent": round(info['memory_percent'] or 0.0, 2),
                "rss_bytes": info['memory_info'].rss if info['memory_info'] else 0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort processes by CPU usage then Memory usage
    sorted_procs = sorted(processes, key=lambda p: (p['cpu_percent'], p['memory_percent']), reverse=True)[:limit]

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "processes_count_total": len(processes),
        "top_processes": sorted_procs
    }

if __name__ == "__main__":
    import json
    print(json.dumps(collect_process_metrics(limit=5), indent=2))
