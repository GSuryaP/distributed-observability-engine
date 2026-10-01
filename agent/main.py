import sys
import os
import time
import logging

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.config import settings
from agent.collectors import (
    collect_host_metrics,
    collect_process_metrics,
    collect_docker_metrics,
    collect_service_metrics
)
from agent.publisher.kafka_publisher import ResilientKafkaPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("nexus_agent")

def run_agent():
    logger.info(f"Starting Nexus Telemetry Agent (Host ID: {settings.HOST_ID})...")
    publisher = ResilientKafkaPublisher(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    
    try:
        while True:
            logger.info("Executing telemetry collection cycle...")
            
            # 1. Collect Host Metrics
            host_data = collect_host_metrics()
            host_data["environment"] = settings.ENVIRONMENT
            publisher.publish(settings.KAFKA_TOPIC_HOST_METRICS, settings.HOST_ID, host_data)
            
            # 2. Collect Process Metrics
            process_data = collect_process_metrics(limit=settings.PROCESS_LIMIT, host_id=settings.HOST_ID)
            publisher.publish(settings.KAFKA_TOPIC_PROCESS_METRICS, settings.HOST_ID, process_data)
            
            # 3. Collect Docker Metrics
            docker_data = collect_docker_metrics(host_id=settings.HOST_ID)
            publisher.publish(settings.KAFKA_TOPIC_SERVICE_METRICS, settings.HOST_ID, docker_data)
            
            # 4. Collect Service Metrics
            service_data = collect_service_metrics(
                host_id=settings.HOST_ID,
                redis_host=settings.REDIS_HOST,
                redis_port=settings.REDIS_PORT,
                postgres_host=settings.POSTGRES_HOST,
                postgres_port=settings.POSTGRES_PORT
            )
            publisher.publish(settings.KAFKA_TOPIC_SERVICE_METRICS, settings.HOST_ID, service_data)
            
            publisher.flush(1.0)
            time.sleep(settings.COLLECTION_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        logger.info("Stopping Nexus Telemetry Agent...")
        publisher.flush(2.0)

if __name__ == "__main__":
    run_agent()
