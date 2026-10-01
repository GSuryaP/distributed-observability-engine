import json
import logging
from typing import Dict, Any

logger = logging.getLogger("kafka_publisher")

class ResilientKafkaPublisher:
    """Publishes telemetry metrics to Kafka topics with fallback logging."""
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        try:
            from confluent_kafka import Producer
            conf = {
                'bootstrap.servers': self.bootstrap_servers,
                'client.id': 'nexus-telemetry-agent',
                'retries': 3,
                'retry.backoff.ms': 500,
                'acks': '1'
            }
            self.producer = Producer(conf)
            logger.info(f"Kafka Producer initialized on {self.bootstrap_servers}")
        except Exception as e:
            logger.warning(f"Failed to connect to Kafka at {self.bootstrap_servers}. Operating in fallback mode: {e}")
            self.producer = None

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

    def publish(self, topic: str, key: str, payload: Dict[str, Any]):
        """Publishes payload to Kafka topic partitioned by key."""
        serialized_payload = json.dumps(payload).encode('utf-8')
        
        if self.producer:
            try:
                self.producer.produce(
                    topic=topic,
                    key=key.encode('utf-8'),
                    value=serialized_payload,
                    callback=self._delivery_report
                )
                self.producer.poll(0)
            except Exception as e:
                logger.error(f"Error sending message to Kafka topic {topic}: {e}")
        else:
            logger.info(f"[KAFKA FALLBACK LOG] Topic: {topic} | Key: {key} | Payload Size: {len(serialized_payload)} bytes")

    def flush(self, timeout: float = 2.0):
        if self.producer:
            self.producer.flush(timeout)
