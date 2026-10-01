.PHONY: help infra-up infra-down agent-run backend-run chaos-cpu

help:
	@echo "Nexus Monitoring & Observability Platform Commands:"
	@echo "  make infra-up    - Start Kafka, InfluxDB, Postgres, Grafana"
	@echo "  make infra-down  - Stop all infrastructure containers"
	@echo "  make agent-run   - Run local Telemetry Agent"
	@echo "  make backend-run - Run FastAPI Backend & Anomaly Service"

infra-up:
	docker compose up -d

infra-down:
	docker compose down


agent-run:
	./venv/bin/python agent/main.py

streaming-run:
	./venv/bin/python streaming/flink_job.py

backend-run:
	./venv/bin/uvicorn backend.app.main:app --reload --port 8000

chaos-run:
	./venv/bin/python chaos/chaos_runner.py --scenario cpu --duration 15

