import uuid

from sqlalchemy import Column, Float, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship

from ..connection import Base
import enum
from typing import Optional

class Device(Base):
    """Device table model."""

    __tablename__ = "devices"

    mac_address = Column(String(17), nullable=False, unique=True, index=True)
    device_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    serial_number = Column(String(255), nullable=True)
    cpu_info = Column(String(255), nullable=True)
    memory_gb = Column(Float, nullable=True)
    architecture = Column(String(255), nullable=True)
    processor = Column(String(255), nullable=True)

    user = relationship("User", back_populates="devices")

    def __repr__(self):
        """String representation of Device."""
        return f"<Device(device_id={self.device_id}, mac_address='{self.mac_address}', user_id='{self.user_id}')>"
    
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
    username = Column(String(255), nullable=False, index=True)  # Added username column
    # ActivityEvent fields
    event = Column(String(255), nullable=True)
    # WindowEvent fields
    window_title = Column(String(255), nullable=True)
    duration = Column(Float, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    user = relationship("User")
    device = relationship("Device")

    def __repr__(self):
        return f"<Event(id={self.id}, user_id={self.user_id}, device_id={self.device_id}, event_type={self.event_type})>"