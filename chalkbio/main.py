from fastapi import FastAPI
# --- IMPORT THE CELERY APP, NOT Celery directly ---
from .core.celery_app import celery_app
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

# Setup Celery periodic tasks
# --- PASS THE IMPORTED CELERY APP ---
setup_periodic_tasks(celery_app)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ChalkBio API"}