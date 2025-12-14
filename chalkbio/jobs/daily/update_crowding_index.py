from ...core.celery_app import celery_app
from ...core.db import SessionLocal
from sqlalchemy import text

@celery_app.task
def refresh_crowding_index_view():
    """Refreshes the mechanism_crowding materialized view."""
    db = SessionLocal()
    try:
        print("Refreshing mechanism_crowding materialized view...")
        db.execute(text("REFRESH MATERIALIZED VIEW mechanism_crowding;"))
        db.commit()
        print("View refreshed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error refreshing view: {e}")
        raise
    finally:
        db.close()
    return "Crowding Index refreshed."