"""Pydantic models for enrollment data structures."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DeviceFingerprint(BaseModel):
    """Hardware fingerprint information for device identification."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    mac_address: str = Field(..., pattern=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", description="MAC address in standard format")
    serial_number: str | None = Field(None, min_length=1, description="Device serial number")
    cpu_info: str | None = Field(None, min_length=1, description="CPU information")
    memory_gb: float | None = Field(None, gt=0, description="Total system memory in GB")
    architecture: str | None = Field(None, min_length=1, description="CPU architecture")
    processor: str | None = Field(None, min_length=1, description="Processor name")


class EnrollmentRequest(BaseModel):
    """Enrollment request data sent to the server."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    username: str = Field(..., min_length=1, description="Username for enrollment")
    user_email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", description="User email address")
    hostname: str | None = Field(None, min_length=1, description="Device hostname")
    platform: str | None = Field(None, min_length=1, description="Platform name")
    device_fingerprint: DeviceFingerprint = Field(..., description="Device hardware fingerprint")


class CredentialValidationRequest(BaseModel):
    """Request model for credential validation."""

    user_email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", description="User email address")
    device_fingerprint: DeviceFingerprint = Field(..., description="Device hardware fingerprint (MAC only)")


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


class DeleteStatus(Enum):
    """Enum representing credential operation outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"
    INVALID_REQUEST = "invalid_request"


class DeleteResponse(BaseModel):
    """Response model for deletion."""

    status: DeleteStatus
    message: str


class UpdateUsernameStatus(Enum):
    """Enum representing credential operation outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"
    INVALID_REQUEST = "invalid_request"


class UpdateUsernameResponse(BaseModel):
    """Response model for updating username."""

    status: UpdateUsernameStatus
    message: str
