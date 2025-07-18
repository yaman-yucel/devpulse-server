from loguru import logger

from devpulse_server.api.credentials.models.credential_models import (
    DeleteResponse,
    DeleteStatus,
    DeviceFingerprint,
    EnrollResponse,
    EnrollStatus,
    UpdateUsernameResponse,
    UpdateUsernameStatus,
    ValidateResponse,
    ValidateStatus,
)
from devpulse_server.database.connection import get_db
from devpulse_server.database.tables.device import Device
from devpulse_server.database.tables.user import User


class CredentialClient:
    """Credentials class."""

    def enroll_credential(self, username: str, user_email: str, device_fingerprint: DeviceFingerprint) -> EnrollResponse:
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

    def delete_user(self, user_email: str) -> DeleteResponse:
        """Delete a user."""
        db = next(get_db())
        try:
            user = db.query(User).filter(User.user_email == user_email).first()
            if user:
                db.delete(user)
                db.commit()
                return DeleteResponse(status=DeleteStatus.SUCCESS, message="User deleted.")
            else:
                return DeleteResponse(status=DeleteStatus.FAILURE, message="User not found.")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return DeleteResponse(status=DeleteStatus.FAILURE, message=f"Error deleting user: {e}")
        finally:
            db.close()

    def update_username(self, user_email: str, username: str) -> UpdateUsernameResponse:
        """Update a user's username."""
        db = next(get_db())
        try:
            user = db.query(User).filter(User.user_email == user_email).first()
            if user:
                user.user_name = username  # type: ignore
                db.commit()
                return UpdateUsernameResponse(status=UpdateUsernameStatus.SUCCESS, message="Username updated.")
            else:
                return UpdateUsernameResponse(status=UpdateUsernameStatus.FAILURE, message="User not found.")
        except Exception as e:
            logger.error(f"Error updating username: {e}")
            return UpdateUsernameResponse(status=UpdateUsernameStatus.FAILURE, message=f"Error updating username: {e}")
        finally:
            db.close()
