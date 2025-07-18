from fastapi import APIRouter

from devpulse_server.credentials.credential import CredentialClient, DeleteResponse, EnrollResponse, ValidateResponse

from .models.credential_models import CredentialValidationRequest, DeleteResponse, EnrollmentRequest, UpdateUsernameResponse

router = APIRouter(prefix="/api/credentials", tags=["credentials"])


@router.post("/enroll")
def enroll_credential(request: EnrollmentRequest) -> EnrollResponse:
    return CredentialClient().enroll_credential(request.username, request.user_email, request.device_fingerprint)


@router.post("/validate")
def validate_credential(request: CredentialValidationRequest) -> ValidateResponse:
    return CredentialClient().validate_credential(request.user_email, request.device_fingerprint)


@router.delete("/delete")  # Very vulnerable, will be admin only feature, auth required
def delete_user(user_email: str) -> DeleteResponse:  # might add Request Model
    return CredentialClient().delete_user(user_email)


@router.put("/update_username")  # Very vulnerable, will be admin only feature, auth required.
def update_username(user_email: str, username: str) -> UpdateUsernameResponse:  # might add Request Model
    return CredentialClient().update_username(user_email, username)
