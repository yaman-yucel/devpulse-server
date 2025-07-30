import uuid

from sqlalchemy import Column, Float, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship

from ..connection import Base
import enum


class EventType(enum.Enum):
    activity = "activity"
    heartbeat = "heartbeat"
    window = "window"
    
class Event(Base):
    """Event table model for storing all event types."""
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    device_id = Column(String(36), ForeignKey("devices.device_id"), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    event = Column(String(255), nullable=True)
    window_title = Column(String(255), nullable=True)
    duration = Column(Float, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    user = relationship("User")
    device = relationship("Device")

    def __repr__(self):
        return f"<Event(id={self.id}, user_id={self.user_id}, device_id={self.device_id}, event_type={self.event_type})>"