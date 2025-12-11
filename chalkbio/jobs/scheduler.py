from celery.schedules import crontab

# This now takes the celery_app object as an argument
def setup_periodic_tasks(celery_app):
    celery_app.conf.beat_schedule = {
        'run-daily-validations': {
            'task': 'chalkbio.jobs.daily.run_validations.run_user_events_validation',
            'schedule': crontab(hour=1, minute=0),
        },
        'run-daily-aggregations': {
            'task': 'chalkbio.jobs.daily.update_aggregations.update_most_watched',
            'schedule': crontab(hour=2, minute=0),
        },
        'retrain-prediction-model': {
            'task': 'chalkbio.jobs.weekly.retrain_model.retrain_trial_success_model',
            'schedule': crontab(day_of_week='sunday', hour=4, minute=0),
        },
    }