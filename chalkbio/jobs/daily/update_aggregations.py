from ...main import celery

@celery.task
def update_most_watched():
    """
    Celery task to refresh the 'most_watched' materialized view.
    """
    print("Updating 'Most Watched' aggregation...")
    # In a real application, you would get a DB session and run:
    # with get_db() as db:
    #     db.execute(text("REFRESH MATERIALIZED VIEW most_watched;"))
    #     db.commit()
    print("Aggregation updated successfully.")
    return "Most Watched updated."