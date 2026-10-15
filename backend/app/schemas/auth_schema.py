from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_password_bytes(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password must not exceed 72 UTF-8 bytes")
    return value


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    password: str = Field(min_length=8, max_length=72)
    referral_code: str | None = Field(default=None, max_length=20)

    _password_bytes = field_validator("password")(validate_password_bytes)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)
    remember_me: bool = True

    _password_bytes = field_validator("password")(validate_password_bytes)


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=10, max_length=8192)
    remember_me: bool = True


class GoogleLinkRequest(BaseModel):
    id_token: str = Field(min_length=10, max_length=8192)
    password: str = Field(min_length=1, max_length=72)

    _password_bytes = field_validator("password")(validate_password_bytes)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    expires_in: int = 900
    session_expires_at: datetime | None = None


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32, max_length=512)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=512)
    new_password: str = Field(min_length=8, max_length=72)

    _password_bytes = field_validator("new_password")(validate_password_bytes)


class MessageResponse(BaseModel):
    message: str


class ReferralSummaryResponse(BaseModel):
    referral_code: str
    referred_count: int
    reward_days: int
