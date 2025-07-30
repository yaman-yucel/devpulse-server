import uuid

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from ..connection import Base

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
    
