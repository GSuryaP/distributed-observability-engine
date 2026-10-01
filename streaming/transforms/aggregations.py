import math
from typing import List, Tuple

def calculate_mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)

def calculate_std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return round(math.sqrt(variance), 2)

def calculate_slope(values: List[float], times: List[float]) -> float:
    """Calculates linear slope (dy/dt) using Least Squares linear regression."""
    n = len(values)
    if n < 2:
        return 0.0
    
    # Normalize times relative to start
    t0 = times[0]
    normalized_times = [t - t0 for t in times]
    
    sum_t = sum(normalized_times)
    sum_y = sum(values)
    sum_tt = sum(t ** 2 for t in normalized_times)
    sum_ty = sum(t * y for t, y in zip(normalized_times, values))
    
    denominator = (n * sum_tt - sum_t ** 2)
    if denominator == 0:
        return 0.0
        
    slope = (n * sum_ty - sum_t * sum_y) / denominator
    return round(slope, 4)

def calculate_min_max(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    return round(min(values), 2), round(max(values), 2)
