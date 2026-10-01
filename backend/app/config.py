import os
from pydantic_settings import BaseSettings

class BackendSettings(BaseSettings):
    PROJECT_NAME: str = "Nexus Observability & Intelligent RCA Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "nexus")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "nexuspassword")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5433")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "nexus_incidents")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    INFLUXDB_URL: str = os.getenv("INFLUXDB_URL", "http://localhost:8087")
    INFLUXDB_TOKEN: str = os.getenv("INFLUXDB_TOKEN", "nexus-secret-token-super-secure")
    INFLUXDB_ORG: str = os.getenv("INFLUXDB_ORG", "nexus-obs")
    INFLUXDB_BUCKET: str = os.getenv("INFLUXDB_BUCKET", "telemetry")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

settings = BackendSettings()
