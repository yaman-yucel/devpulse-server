"""User table model."""

import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from ..connection import Base


class User(Base):
    """User table model."""

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    # full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False, index=True)  # New field for storing hashed password
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of User."""
        return f"<User(username='{self.username}', email='{self.email}')>"
