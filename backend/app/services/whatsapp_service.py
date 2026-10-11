import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import get_settings


def _normalize_nigerian_number(phone: str) -> str:
    """Meta's WhatsApp Cloud API requires E.164 digits with no leading '+'. The
    phone field is free text, so normalize the common Nigerian input shapes
    (0801..., 234801..., +234801...) instead of rejecting anything non-standard."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0"):
        return "234" + digits[1:]
    return digits


def send_whatsapp_message(*, to_phone: str, body: str) -> None:
    settings = get_settings()
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id:
        raise RuntimeError("WhatsApp delivery is not configured")

    url = f"https://graph.facebook.com/{settings.whatsapp_api_version}/{settings.whatsapp_phone_number_id}/messages"
    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": _normalize_nigerian_number(to_phone),
            "type": "text",
            "text": {"body": body},
        }
    ).encode("utf-8")
    request = Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            if response.status not in {200, 201}:
                raise RuntimeError(f"WhatsApp delivery failed with status {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"WhatsApp delivery failed with status {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("WhatsApp delivery could not reach the provider") from exc
