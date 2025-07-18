from enum import Enum

from loguru import logger
from pydantic import BaseModel

from devpulse_server.api.credentials.models.credential_models import DeviceFingerprint
from devpulse_server.database.connection import get_db
from devpulse_server.database.tables.device import Device
from devpulse_server.database.tables.user import User


class EnrollStatus(Enum):
    """Enum representing credential operation outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"
    ALREADY_EXISTS = "already_exists"
    INVALID_REQUEST = "invalid_request"


class EnrollResponse(BaseModel):
    """Response model for enrollment."""

    status: EnrollStatus
    message: str


class ValidateStatus(Enum):
    """Enum representing credential operation outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"
    INVALID_REQUEST = "invalid_request"


class ValidateResponse(BaseModel):
    """Response model for validation."""

    status: ValidateStatus
    message: str


class CredentialClient:
    """Credentials class."""

    def enroll_credential(self, username: str, user_email: str, device_fingerprint: DeviceFingerprint) -> EnrollResponse:
        """Enroll a new credential with user-device logic."""
        db = next(get_db())
        try:
            user = db.query(User).filter(User.user_email == user_email).first()
            device = db.query(Device).filter(Device.mac_address == device_fingerprint.mac_address).first()

            if device and not user:
                logger.info(f"Device {device_fingerprint.mac_address} exists but user {user_email} does not. Invalid request.")
                return EnrollResponse(status=EnrollStatus.INVALID_REQUEST, message="Device exists but user does not. Invalid request.")

            if user and device:
                logger.info(f"User {user_email} and device {device_fingerprint.mac_address} already enrolled.")
                return EnrollResponse(status=EnrollStatus.ALREADY_EXISTS, message="User and device already enrolled.")

            if not user and not device:
                # Add user
                user = User(user_name=username, user_email=user_email)
                db.add(user)
                db.commit()
                db.refresh(user)
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
                db.commit()
                db.refresh(device)
                logger.info(f"Added user {user_email} and device {device_fingerprint.mac_address}.")
                return EnrollResponse(status=EnrollStatus.SUCCESS, message="User and device enrolled.")

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
                db.commit()
                db.refresh(device)
                logger.info(f"Added device {device_fingerprint.mac_address} for user {user_email}.")
                return EnrollResponse(status=EnrollStatus.SUCCESS, message="Device enrolled for existing user.")
            return EnrollResponse(status=EnrollStatus.FAILURE, message="Unknown error in enrollment logic.")
        except Exception as e:
            logger.error(f"Error enrolling credential: {e}")
            db.rollback()
            return EnrollResponse(status=EnrollStatus.FAILURE, message=f"Error enrolling credential: {e}")
        finally:
            db.close()

    def validate_credential(self, user_email: str, device_fingerprint: DeviceFingerprint) -> ValidateResponse:
        """Validate a credential."""
        db = next(get_db())
        try:
            device = db.query(Device).filter(Device.mac_address == device_fingerprint.mac_address).first()
            user = db.query(User).filter(User.user_email == user_email).first()
            if device is not None and user is not None:
                if getattr(device, "user_id", None) == getattr(user, "user_id", None):
                    return ValidateResponse(status=ValidateStatus.SUCCESS, message="Credential validated.")
                else:
                    return ValidateResponse(status=ValidateStatus.FAILURE, message="Device does not belong to user. Enroll the device first.")
            else:
                return ValidateResponse(status=ValidateStatus.FAILURE, message="Device or user not found.")
        except Exception as e:
            logger.error(f"Error validating credential: {e}")
            return ValidateResponse(status=ValidateStatus.FAILURE, message=f"Error validating credential: {e}")
        finally:
            db.close()
