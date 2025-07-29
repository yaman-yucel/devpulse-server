from dataclasses import dataclass

from fastapi import HTTPException
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from devpulse_server.api.credentials.models.credential_models import DeviceFingerprint
from devpulse_server.database.connection import get_db
from devpulse_server.database.tables.device import Device
from devpulse_server.database.tables.user import User


@dataclass
class CredentialClient:
    """Credentials class."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def enroll_credential(self, username: str, password: str, email: str, device_fingerprint: DeviceFingerprint) -> bool:
        async for db in get_db():
            try:
                user = (await db.execute(select(User).where(User.username == username))).scalars().first()
                device = (await db.execute(select(Device).where(Device.mac_address == device_fingerprint.mac_address))).scalars().first()

                if device and not user:
                    logger.info(f"Device {device_fingerprint.mac_address} exists but user {username} does not. Invalid request.")
                    return False

                if user and device:
                    logger.info(f"User {username} and device {device_fingerprint.mac_address} already enrolled.")
                    return False

                if not user and not device:
                    # Add user with hashed password
                    password_hash = self.pwd_context.hash(password)
                    user = User(
                        username=username,
                        email=email,
                        hashed_password=password_hash,
                        is_active=True,
                        is_admin=False,
                    )
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                    # Add device linked to user
                    device = Device(
                        mac_address=device_fingerprint.mac_address,
                        user_id=user.user_id,
                        serial_number=device_fingerprint.serial_number,
                        cpu_info=device_fingerprint.cpu_info,
                        memory_gb=device_fingerprint.memory_gb,
                        architecture=device_fingerprint.architecture,
                        processor=device_fingerprint.processor,
                    )
                    db.add(device)
                    await db.commit()
                    await db.refresh(device)
                    logger.info(f"Added user {username} and device {device_fingerprint.mac_address}.")
                    return True
                
                if user and not device:
                    # Add device linked to user
                    device = Device(
                        mac_address=device_fingerprint.mac_address,
                        user_id=user.user_id,
                        serial_number=device_fingerprint.serial_number,
                        cpu_info=device_fingerprint.cpu_info,
                        memory_gb=device_fingerprint.memory_gb,
                        architecture=device_fingerprint.architecture,
                        processor=device_fingerprint.processor,
                    )
                    db.add(device)
                    await db.commit()
                    await db.refresh(device)
                    logger.info(f"Added device {device_fingerprint.mac_address} for user {email}.")
                    return True
                return False
            except Exception as e:
                logger.error(f"Error enrolling credential: {e}")
                await db.rollback()
                return False
                

    async def authenticate_user(self, username: str, plain_password: str, device_fingerprint: DeviceFingerprint):
        
        async for db in get_db():
            try:
                device = (await db.execute(select(Device).where(Device.mac_address == device_fingerprint.mac_address))).scalars().first()
                user = (await db.execute(select(User).where(User.username == username))).scalars().first()
                if device is not None and user is not None:
                    if device.user_id == user.user_id:
                        if self._verify_password(plain_password, user.hashed_password):
                            return user
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            except Exception as e:
                logger.error(f"Error authenticating user: {e}")
                return None
                

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, plain_password: str) -> str:
        return self.pwd_context.hash(plain_password)
