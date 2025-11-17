from fastapi import FastAPI
from celery import Celery
from .core.config import settings
from .api.endpoints import predictions, investigators
from .jobs.scheduler import setup_periodic_tasks

# FastAPI App Initialization
app = FastAPI(
    title="ChalkBio Data Intelligence API",
    description="API for serving competitive intelligence insights.",
    version="1.0.0"
)

# Include API routers
app.include_router(predictions.router, prefix="/api", tags=["Predictions"])
app.include_router(investigators.router, prefix="/api", tags=["Investigators"])

# Celery Initialization
celery = Celery(
    __name__,
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Setup Celery periodic tasks
setup_periodic_tasks(celery)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ChalkBio API"}