from ...core.celery_app import celery_app
from ...core.db import SessionLocal
from ...models.orm import Watchlist, Alert
import uuid

@celery_app.task
def trigger_fda_alert(drug_id: str, approval_message: str):
    """
    Finds users watching a drug and creates an alert for them.
    """
    db = SessionLocal()
    try:
        print(f"Triggering FDA alert for drug: {drug_id}")
        # Find all user_ids watching this drug
        watchers = db.query(Watchlist.user_id).filter(
            Watchlist.entity_id == drug_id,
            Watchlist.entity_type == 'drug',
            Watchlist.removed_at == None
        ).distinct().all()

        user_ids = [w[0] for w in watchers]
        if not user_ids:
            print("No users watching this drug.")
            return "No alerts created."

        # Create a new alert object for each user
        new_alerts = [
            Alert(
                user_id=user_id,
                entity_id=drug_id,
                entity_type='drug',
                alert_type='fda_action',
                title=f'FDA Update for {drug_id}',
                message=approval_message
            ) for user_id in user_ids
        ]
        
        db.add_all(new_alerts)
        db.commit()
        print(f"Created {len(new_alerts)} alerts.")
        return f"Created {len(new_alerts)} alerts."
    except Exception as e:
        db.rollback()
        print(f"Error triggering alert: {e}")
        raise
    finally:
        db.close()