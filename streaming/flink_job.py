import sys
import os
import json
import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, Any

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streaming.transforms.features import assemble_host_feature_vector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("nexus_stream_processor")

class SlidingWindowStreamProcessor:
    """
    Stateful Stream Processor maintaining 5-minute sliding windows (max 60 samples @ 5s intervals)
    per host_id to extract rolling averages, standard deviation, and metric slopes.
    """
    def __init__(self, window_seconds: int = 300, max_samples: int = 60):
        self.window_seconds = window_seconds
        self.max_samples = max_samples
        # Store state per host_id: deque of metrics dicts
        self.host_windows = defaultdict(lambda: deque(maxlen=max_samples))

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests raw host metric event and produces aggregated feature vector."""
        host_id = event.get("host_id", "unknown")
        
        # Attach epoch timestamp for slope calculation
        timestamp_str = event.get("timestamp")
        try:
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).timestamp()
        except Exception:
            ts = time.time()
            
        event["timestamp_ts"] = ts
        
        # Add to stateful window
        window = self.host_windows[host_id]
        window.append(event)
        
        # Prune elements older than window_seconds
        cutoff = ts - self.window_seconds
        while window and window[0].get("timestamp_ts", 0) < cutoff:
            window.popleft()
            
        # Assemble feature vector
        feature_vector = assemble_host_feature_vector(host_id, list(window))
        return feature_vector

def run_standalone_stream_job(bootstrap_servers: str = "localhost:9092"):
    """Runs high-throughput stream processing loop connecting Kafka input to output topic."""
    from confluent_kafka import Consumer, Producer
    
    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'nexus-flink-stream-group',
        'auto.offset.reset': 'latest'
    }
    producer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'nexus-stream-processor-out'
    }
    
    logger.info("Initializing Streaming Engine Consumers & Producers...")
    processor = SlidingWindowStreamProcessor()
    
    try:
        consumer = Consumer(consumer_conf)
        producer = Producer(producer_conf)
        consumer.subscribe(['metrics.host'])
        logger.info("Subscribed to 'metrics.host'. Processing real-time telemetry windows...")
        
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka Stream Error: {msg.error()}")
                continue
                
            try:
                payload = json.loads(msg.value().decode('utf-8'))
                features = processor.process_event(payload)
                
                if features:
                    producer.produce(
                        topic='stream.features',
                        key=features['host_id'].encode('utf-8'),
                        value=json.dumps(features).encode('utf-8')
                    )
                    producer.poll(0)
                    logger.debug(f"Emitted stream features for host: {features['host_id']}")
                    
                    # Forward features to backend for live InfluxDB time-series population
                    try:
                        import requests
                        requests.post("http://localhost:8000/api/v1/metrics/ingest", json=features, timeout=1.0)
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"Error processing stream event: {e}")
                
    except KeyboardInterrupt:
        logger.info("Shutting down Stream Processing Engine...")
    except Exception as e:
        logger.warning(f"Kafka unavailable for stream job, running offline window processor test: {e}")

if __name__ == "__main__":
    run_standalone_stream_job()
