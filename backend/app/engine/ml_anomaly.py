import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger("ml_anomaly_engine")

class MLAnomalyDetector:
    """Stage 2 Machine Learning Anomaly Detector using Isolation Forest."""
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False
        self._bootstrap_synthetic_baseline()

    def _bootstrap_synthetic_baseline(self):
        """Generates healthy synthetic operational baseline data to fit the model initially."""
        np.random.seed(42)
        # Features: [cpu_mean, cpu_std, cpu_slope, memory_mean, net_tx, net_rx]
        normal_cpu = np.random.normal(loc=35.0, scale=10.0, size=500)
        normal_cpu_std = np.random.normal(loc=2.0, scale=0.5, size=500)
        normal_slope = np.random.normal(loc=0.0, scale=0.05, size=500)
        normal_mem = np.random.normal(loc=50.0, scale=8.0, size=500)
        normal_tx = np.random.normal(loc=1000000, scale=200000, size=500)
        normal_rx = np.random.normal(loc=2000000, scale=400000, size=500)
        
        X_train = np.column_stack([normal_cpu, normal_cpu_std, normal_slope, normal_mem, normal_tx, normal_rx])
        self.model.fit(X_train)
        self.is_fitted = True
        logger.info("ML Anomaly IsolationForest model bootstrapped with synthetic baseline data.")

    def predict_anomaly(self, features_dict: Dict[str, Any]) -> Tuple[float, bool]:
        """
        Predicts anomaly score S in [0.0, 1.0] and returns boolean anomaly status.
        Higher score implies higher anomaly severity.
        """
        if not self.is_fitted:
            return 0.0, False
            
        vector = np.array([[
            features_dict.get("cpu_mean_5m", 0.0),
            features_dict.get("cpu_std_5m", 0.0),
            features_dict.get("cpu_slope_1m", 0.0),
            features_dict.get("memory_mean_5m", 0.0),
            features_dict.get("net_tx_throughput_bytes", 0.0),
            features_dict.get("net_rx_throughput_bytes", 0.0)
        ]])
        
        # Decision function: lower values mean more anomalous
        raw_score = self.model.decision_function(vector)[0]
        # Map decision score to [0.0, 1.0] scale where > 0.75 is anomalous
        anomaly_score = round(float(1.0 / (1.0 + np.exp(raw_score * 5.0))), 4)
        is_anomalous = anomaly_score >= 0.70
        
        return anomaly_score, is_anomalous

ml_detector = MLAnomalyDetector()
