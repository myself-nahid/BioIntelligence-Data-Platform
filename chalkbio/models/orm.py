from sqlalchemy import Column, String, JSON, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
# --- CHANGE THIS LINE ---
from sqlalchemy.orm import declarative_base

# Create a base class for our models to inherit from
Base = declarative_base()

class UserEvent(Base):
    __tablename__ = "user_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_type = Column(String(20), nullable=False)
    event_type = Column(String(50), nullable=False)
    entity_id = Column(String(100))
    entity_type = Column(String(50))
    # --- CHANGE THIS LINE ---
    # Renamed to avoid clashing with SQLAlchemy's reserved 'metadata' attribute
    metadata_ = Column("metadata", JSON) 
    request_id = Column(UUID(as_uuid=True))
    event_version = Column(String(10), default='v1.0')
    schema_version = Column(String(10), default='s1.0')
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())