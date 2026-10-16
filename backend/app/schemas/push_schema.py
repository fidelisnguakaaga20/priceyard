from pydantic import BaseModel, Field, field_validator

from app.utils.push_validation import validate_push_endpoint, validate_push_key


class PushSubscriptionKeys(BaseModel):
    p256dh: str = Field(min_length=1, max_length=300)
    auth: str = Field(min_length=1, max_length=100)

    @field_validator("p256dh")
    @classmethod
    def public_key_is_valid(cls, value: str) -> str:
        return validate_push_key(value, public=True)

    @field_validator("auth")
    @classmethod
    def authentication_key_is_valid(cls, value: str) -> str:
        return validate_push_key(value, public=False)


class PushSubscriptionCreate(BaseModel):
    endpoint: str = Field(min_length=1, max_length=500)
    keys: PushSubscriptionKeys

    @field_validator("endpoint")
    @classmethod
    def destination_is_valid(cls, value: str) -> str:
        return validate_push_endpoint(value)


class PushUnsubscribeRequest(BaseModel):
    endpoint: str = Field(min_length=1, max_length=500)
