# Nexus Platform Technical Architecture Specification

## 1. Metric Schema Specification

All metrics published to Kafka follow a normalized JSON structure:

```json
{
  "timestamp": "2026-10-01T16:30:00.000Z",
  "host_id": "node-prod-01",
  "environment": "production",
  "metrics": {
    "cpu_utilization_percent": 88.4,
    "cpu_iowait_percent": 12.1,
    "memory_used_percent": 79.2,
    "disk_io_read_bytes_sec": 52428800,
    "disk_io_write_bytes_sec": 10485760,
    "net_tx_bytes_sec": 1205000,
    "net_rx_bytes_sec": 4500000
  }
}
```

---

## 2. Stream Processing Mathematics

### Moving Average ($\mu$)
$$\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$$

### Moving Standard Deviation ($\sigma$)
$$\sigma = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (x_i - \mu)^2}$$

### Metric Linear Slope ($\Delta y / \Delta t$)
Calculated via Ordinary Least Squares (OLS) linear regression over normalized window time steps $t_i$:

$$\text{Slope} = \frac{N \sum (t_i y_i) - (\sum t_i)(\sum y_i)}{N \sum (t_i^2) - (\sum t_i)^2}$$

Where positive slope indicates rising resource consumption pressure.

---

## 3. Machine Learning Anomaly Score Equation

The Stage 2 Anomaly Detector uses an **Isolation Forest** model evaluating scaled feature vectors:

$$X = [\mu_{\text{cpu}}, \sigma_{\text{cpu}}, \text{Slope}_{\text{cpu}}, \mu_{\text{mem}}, \text{Net}_{\text{tx}}, \text{Net}_{\text{rx}}]$$

The raw decision score $s(x, n)$ is mapped into a normalized probability score $S \in [0.0, 1.0]$ using a sigmoid transformation:

$$S = \frac{1}{1 + e^{-5 \cdot d(x)}}$$

Where $S \ge 0.70$ classifies the window state as **ANOMALOUS**.

---

## 4. Root Cause Causal Confidence Matrix

When an incident triggers at a symptom node $N_{\text{symptom}}$, the RCA engine evaluates candidate nodes $N$ in the downstream dependency graph $G = (V, E)$:

$$\text{Confidence}(N) = w_1 \cdot \text{AnomalyScore}(N) + w_2 \cdot d(N_{\text{symptom}}, N) + w_3 \cdot P_{\text{temporal}}(N)$$

Where:
* $w_1 = 0.5$, $w_2 = 0.2$, $w_3 = 0.3$
* $d(N_{\text{symptom}}, N)$ is the shortest path distance in the dependency graph.
* $P_{\text{temporal}}(N) = 1.0$ if alert on $N$ preceded or coincided with $N_{\text{symptom}}$.
