from datetime import datetime, timezone
import logging

logger = logging.getLogger("docker_collector")

def collect_docker_metrics(host_id: str = "host-prod-01"):
    """Collects container metrics via Docker Engine Socket if available."""
    container_metrics = []
    
    try:
        import docker
        client = docker.from_env(timeout=2)
        containers = client.containers.list(all=True)
        
        for c in containers:
            stats = None
            cpu_pct = 0.0
            mem_used = 0
            mem_limit = 0
            
            if c.status == "running":
                try:
                    # Stream stats non-blocking single shot
                    raw_stats = c.stats(stream=False)
                    mem_used = raw_stats.get('memory_stats', {}).get('usage', 0)
                    mem_limit = raw_stats.get('memory_stats', {}).get('limit', 1)
                    
                    # Calculate CPU % delta
                    cpu_stats = raw_stats.get('cpu_stats', {})
                    precpu_stats = raw_stats.get('precpu_stats', {})
                    
                    cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
                    system_delta = cpu_stats.get('system_cpu_usage', 0) - precpu_stats.get('system_cpu_usage', 0)
                    online_cpus = cpu_stats.get('online_cpus', 1)
                    
                    if system_delta > 0 and cpu_delta > 0:
                        cpu_pct = round((cpu_delta / system_delta) * online_cpus * 100.0, 2)
                except Exception as e:
                    logger.debug(f"Failed to fetch stats for container {c.name}: {e}")
            
            container_metrics.append({
                "container_id": c.short_id,
                "name": c.name,
                "image": c.image.tags[0] if c.image.tags else "unknown",
                "status": c.status,
                "cpu_percent": cpu_pct,
                "memory_used_bytes": mem_used,
                "memory_limit_bytes": mem_limit,
                "memory_percent": round((mem_used / mem_limit) * 100.0, 2) if mem_limit > 0 else 0.0
            })
    except Exception as e:
        logger.warning(f"Docker SDK unavailable or daemon not running: {e}")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "containers_count": len(container_metrics),
        "containers": container_metrics
    }

if __name__ == "__main__":
    import json
    print(json.dumps(collect_docker_metrics(), indent=2))
