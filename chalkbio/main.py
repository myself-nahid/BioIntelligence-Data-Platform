from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.celery_app import celery_app
from .api.endpoints import predictions, investigators, events, watchlists, alerts, crowding
from .jobs.scheduler import setup_periodic_tasks
from .models import predict
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    print("Application startup: Loading ML model assets...")
    predict.load_prediction_assets()
    yield
    # This code runs on shutdown (optional)
    print("Application shutdown.")

app = FastAPI(
    title="ChalkBio Data Intelligence API",
    description="API for serving competitive intelligence insights.",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "https://automation.chalkbio.com",
    "https://dashboard.chalkbio.com",
    "https://api.chalkbio.com",
    "https://chalkbio.com",

    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(predictions.router, prefix="/api", tags=["Predictions"])
app.include_router(investigators.router, prefix="/api", tags=["Investigators"])
app.include_router(events.router, prefix="/api", tags=["Events"])
app.include_router(watchlists.router, prefix="/api", tags=["Watchlists"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(crowding.router, prefix="/api", tags=["Crowding"])

# Setup Celery periodic tasks
setup_periodic_tasks(celery_app)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ChalkBio API"}