from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    status = await client.enroll_credential(request.username, request.password, request.user_email, request.device_fingerprint)
    return {"status": status}


@router.post("/token")
async def login(client: Annotated[CredentialClient, Depends(CredentialClient)], login_data: LoginRequest):

    device_fingerprint = DeviceFingerprint(mac_address=login_data.mac_address)
    user = await client.authenticate_user(login_data.username, login_data.password, device_fingerprint)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, or device not recognized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if login_data.never_expires:
        if not ALLOW_NEVER_EXPIRING_TOKENS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Non-expiring tokens are not allowed")
        access_token = create_access_token(data={"sub": user.username, "device_mac": device_fingerprint.mac_address}, never_expires=True)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username, "device_mac": device_fingerprint.mac_address}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer", "expires": not login_data.never_expires}


async def get_current_user_and_device(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)) -> tuple[User, Device]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") is not None:
            if payload.get("exp") < datetime.now(timezone.utc).timestamp():
                raise HTTPException(status_code=401, detail="Token expired")
        user = (await db.execute(
            select(User).where(User.username == payload["sub"]))
        ).scalars().first()
        device = (await db.execute(
            select(Device).where(Device.mac_address == payload.get("device_mac")))
        ).scalars().first()
        if not user or device.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="Invalid credentials or device")
        return user, device
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

