from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic_settings import BaseSettings

from devpulse_server.api.credentials.models.credential_models import DeviceFingerprint, LoginRequest, SignupRequest
from devpulse_server.credentials.credential import CredentialClient
from devpulse_server.database.connection import get_db
from devpulse_server.database.tables.device import Device
from devpulse_server.database.tables.user import User


class Settings(BaseSettings):
    secret_key: str = "05607e3f1e3ce53fa1881c4a367db47769aee1665e695be23f2d1e6bd418bf8f"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allow_never_expiring_tokens: bool = True

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"


settings = Settings()


# JWT Configuration
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
ALLOW_NEVER_EXPIRING_TOKENS = settings.allow_never_expiring_tokens

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/credentials/token")

router = APIRouter(prefix="/api/credentials", tags=["credentials"])


def create_access_token(data: dict, expires_delta: timedelta | None = None, never_expires: bool = False) -> str:
    """Create JWT access token with optional expiration."""
    to_encode = data.copy()

    if never_expires:
        # Don't add expiration claim - token will never expire
        pass
    elif expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/signup")
async def signup(request: SignupRequest, client: Annotated[CredentialClient, Depends(CredentialClient)]) -> dict[str, bool]:
    """Sign up a new user with device validation."""
    status = client.enroll_credential(request.username, request.password, request.user_email, request.device_fingerprint)
    return {"status": status}


@router.post("/token")
async def login(client: Annotated[CredentialClient, Depends(CredentialClient)], login_data: LoginRequest):
    """Login endpoint that returns JWT token with device validation."""

    # Create device fingerprint with only MAC address
    device_fingerprint = DeviceFingerprint(mac_address=login_data.mac_address)
    # Authenticate user with device validation
    user = client.authenticate_user(login_data.username, login_data.password, device_fingerprint)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, or device not recognized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with optional expiration
    if login_data.never_expires:
        if not ALLOW_NEVER_EXPIRING_TOKENS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Non-expiring tokens are not allowed")
        access_token = create_access_token(data={"sub": user.username, "device_mac": device_fingerprint.mac_address}, never_expires=True)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username, "device_mac": device_fingerprint.mac_address}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer", "expires": not login_data.never_expires}


async def get_current_user_and_device(token: Annotated[str, Depends(oauth2_scheme)], db=Depends(get_db)) -> tuple[User, Device]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") is not None:
            if payload.get("exp") < datetime.now(timezone.utc).timestamp():
                raise HTTPException(status_code=401, detail="Token expired")
        user = db.query(User).filter(User.username == payload["sub"]).first()
        device = db.query(Device).filter(Device.mac_address == payload.get("device_mac")).first()
        if not user or device.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="Invalid credentials or device")
        return user, device
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/user")
async def get_user(user_device: Annotated[tuple[User, Device], Depends(get_current_user_and_device)]):
    user, device = user_device
    return {"user": user, "device": device}


# @router.post("/admin/create-permanent-token")
# async def create_permanent_token(username: str, device_mac: str, request: Request, current_admin: Annotated[User, Depends(get_current_active_admin)]):
#     """Admin endpoint to create a permanent (never-expiring) token for a user and device."""
#     client = CredentialClient()

#     # Verify the target user exists
#     user = client.get_user_by_username(username)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     # Create permanent token with device MAC
#     access_token = create_access_token(data={"sub": user.username, "device_mac": device_mac}, never_expires=True)

#     return {"access_token": access_token, "token_type": "bearer", "expires": False, "user": username, "device_mac": device_mac, "created_by": current_admin.username}


# @router.delete("/delete")  # Very vulnerable, will be admin only feature, auth required
# def delete_user(user_email: str) -> DeleteResponse:  # might add Request Model
#     return CredentialClient().delete_user(user_email)


# @router.put("/update_username")  # Very vulnerable, will be admin only feature, auth required.
# def update_username(user_email: str, username: str) -> UpdateUsernameResponse:  # might add Request Model
#     return CredentialClient().update_username(user_email, username)
