from fastapi import APIRouter

from devpulse_server.credentials.credential import CredentialClient, EnrollResponse, ValidateResponse

from .models.credential_models import CredentialValidationRequest, EnrollmentRequest

router = APIRouter(prefix="/api/credentials", tags=["credentials"])


@router.post("/enroll")
def enroll_credential(request: EnrollmentRequest) -> EnrollResponse:
    """Enroll a new credential."""
    response = CredentialClient().enroll_credential(request.username, request.user_email, request.device_fingerprint)
    return response


@router.post("/validate")
def validate_credential(request: CredentialValidationRequest) -> ValidateResponse:
    response = CredentialClient().validate_credential(request.user_email, request.device_fingerprint)
    return response
