import os
from pydantic_settings import BaseSettings

class AgentSettings(BaseSettings):
    AGENT_ID: str = os.getenv("AGENT_ID", "agent-node-01")
    HOST_ID: str = os.getenv("HOST_ID", "host-prod-01")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_HOST_METRICS: str = os.getenv("KAFKA_TOPIC_HOST_METRICS", "metrics.host")
    KAFKA_TOPIC_PROCESS_METRICS: str = os.getenv("KAFKA_TOPIC_PROCESS_METRICS", "metrics.process")
    KAFKA_TOPIC_SERVICE_METRICS: str = os.getenv("KAFKA_TOPIC_SERVICE_METRICS", "metrics.service")
    KAFKA_TOPIC_APP_METRICS: str = os.getenv("KAFKA_TOPIC_APP_METRICS", "metrics.application")
    
    COLLECTION_INTERVAL_SECONDS: int = int(os.getenv("COLLECTION_INTERVAL_SECONDS", "5"))
    PROCESS_LIMIT: int = int(os.getenv("PROCESS_LIMIT", "10"))
    
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5433"))

settings = AgentSettings()
