"""User table model."""

import uuid

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..connection import Base


class User(Base):
    """User table model."""

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_name = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False, unique=True, index=True)

    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of User."""
        return f"<User(user_id={self.user_id}, user_name='{self.user_name}', user_email='{self.user_email}')>"
