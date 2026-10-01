from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.app.config import settings
from backend.app.db.postgres import init_db
from backend.app.api import incidents, topology, rca, metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_backend")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Distributed Observability, Stream Processing, Anomaly Detection & RCA Engine API"
)

# Enable CORS for Grafana and local web UIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Nexus Backend Service running cleanly.")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Mount static directory for Dashboard UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_dashboard_ui():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Nexus Backend API is running."}

@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Register API routers
app.include_router(incidents.router, prefix=settings.API_V1_STR)
app.include_router(topology.router, prefix=settings.API_V1_STR)
app.include_router(rca.router, prefix=settings.API_V1_STR)
app.include_router(metrics.router, prefix=settings.API_V1_STR)
