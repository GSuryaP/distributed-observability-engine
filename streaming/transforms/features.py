from typing import List, Dict, Any
from datetime import datetime, timezone
from streaming.transforms.aggregations import calculate_mean, calculate_std, calculate_slope, calculate_min_max

def assemble_host_feature_vector(host_id: str, window_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Transforms raw windowed host telemetry events into a structured feature vector.
    `window_data` is a list of metrics dictionaries sorted by timestamp.
    """
    if not window_data:
        return {}

    timestamps = [d.get("timestamp_ts", 0.0) for d in window_data]
    cpu_vals = [d["metrics"].get("cpu_utilization_percent", 0.0) for d in window_data]
    mem_vals = [d["metrics"].get("memory_used_percent", 0.0) for d in window_data]
    iowait_vals = [d["metrics"].get("cpu_iowait_percent", 0.0) for d in window_data]
    net_tx_vals = [d["metrics"].get("net_bytes_sent", 0) for d in window_data]
    net_rx_vals = [d["metrics"].get("net_bytes_recv", 0) for d in window_data]

    cpu_min, cpu_max = calculate_min_max(cpu_vals)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host_id": host_id,
        "sample_count": len(window_data),
        "features": {
            "cpu_mean_5m": calculate_mean(cpu_vals),
            "cpu_std_5m": calculate_std(cpu_vals),
            "cpu_slope_1m": calculate_slope(cpu_vals, timestamps),
            "cpu_min_5m": cpu_min,
            "cpu_max_5m": cpu_max,
            "memory_mean_5m": calculate_mean(mem_vals),
            "memory_std_5m": calculate_std(mem_vals),
            "iowait_mean_5m": calculate_mean(iowait_vals),
            "net_tx_throughput_bytes": calculate_mean(net_tx_vals),
            "net_rx_throughput_bytes": calculate_mean(net_rx_vals)
        }
    }
