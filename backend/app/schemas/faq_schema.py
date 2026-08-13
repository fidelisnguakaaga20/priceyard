from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Stage 14 content guardrails implement the approved rules that can be
# checked locally. Word-for-word copying from a paid source still requires
# human/editorial verification because PriceYard does not store that source
# corpus for automated comparison.
_POSITIVE_GUARANTEE_PATTERNS = (
    re.compile(r"\bprofit\s+(?:is|will\s+be)\s+guaranteed\b", re.IGNORECASE),
    re.compile(r"\bguaranteed\s+(?:profit|buying\s+opportunity|selling\s+opportunity)\b", re.IGNORECASE),
    re.compile(r"\byou\s+(?:cannot|can't)\s+lose\b", re.IGNORECASE),
    re.compile(r"\bprice\s+will\s+surely\s+rise\b", re.IGNORECASE),
    re.compile(r"\bprice\s+is\s+certain\s+to\s+rise\b", re.IGNORECASE),
    re.compile(r"\byou\s+must\s+(?:buy|sell)\b", re.IGNORECASE),
    re.compile(r"\bthis\s+is\s+financial\s+advice\b", re.IGNORECASE),
    re.compile(r"\b100\s*%\s+(?:profit|return)\b", re.IGNORECASE),
)
_PRIVATE_PHONE_PATTERN = re.compile(r"(?:\+?234|0)[\s-]?[789]\d(?:[\s-]?\d){8}\b")
_PRIVATE_ACCOUNT_PATTERN = re.compile(
    r"\b(?:account(?:\s+number)?|acct|bank\s+account|pay\s+to|transfer\s+to)\b[^\n.]{0,60}\b\d{10,18}\b",
    re.IGNORECASE,
)
_VENDOR_INSTRUCTION_PATTERN = re.compile(
    r"\b(?:call|contact|whatsapp)\s+(?:this\s+)?(?:vendor|seller|coach)\b[^\n.]{0,80}",
    re.IGNORECASE,
)


def validate_faq_content(value: str) -> str:
    for pattern in _POSITIVE_GUARANTEE_PATTERNS:
        if pattern.search(value):
            raise ValueError("FAQ content must not contain guarantees, financial advice, or forced buy/sell instructions")
    if _PRIVATE_PHONE_PATTERN.search(value) or _PRIVATE_ACCOUNT_PATTERN.search(value):
        raise ValueError("FAQ content must not contain private phone or account-number instructions")
    if _VENDOR_INSTRUCTION_PATTERN.search(value):
        raise ValueError("FAQ content must not contain private vendor contact instructions")
    return value


class FAQCreate(BaseModel):
    question: str = Field(min_length=3)
    answer: str = Field(min_length=3)
    category: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("question", "answer")
    @classmethod
    def content_must_be_safe(cls, value: str) -> str:
        return validate_faq_content(value)


class FAQUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=3)
    answer: str | None = Field(default=None, min_length=3)
    category: str | None = Field(default=None, min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("question", "answer")
    @classmethod
    def content_must_be_safe(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_faq_content(value)


class FAQAdminResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str
    is_published: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FAQPublicResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
