from sqlalchemy.orm import Session

from devpulse_server.database.connection import Base, engine
from devpulse_server.database.tables.device import Device
from devpulse_server.database.tables.user import User
from loguru import logger


def add_sample_data() -> None:
    """Add sample Device and User to the database if not present."""
    with Session(engine) as session:
        # Add sample device
        if not session.query(Device).first():
            device = Device(mac_address="00:11:22:33:44:55")
            session.add(device)
            logger.info(f"Sample device added: {device}")
        # Add sample user
        if not session.query(User).first():
            user = User(user_name="Sample User", user_email="sample@example.com")
            session.add(user)
            logger.info(f"Sample user added: {user}")
        session.commit()
