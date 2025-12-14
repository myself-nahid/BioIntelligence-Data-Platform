from celery import Celery
from .config import settings

# Create the central Celery application object
celery_app = Celery(
    "chalkbio", # You can name this anything, but the project name is conventional
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[ # Add the paths to all your task modules here
        'chalkbio.jobs.daily.run_validations',
        'chalkbio.jobs.daily.update_aggregations',
        'chalkbio.jobs.weekly.retrain_model',
        'chalkbio.jobs.daily.update_crowding_index',
        'chalkbio.jobs.triggers.fda_alerts',
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)