from email.message import EmailMessage
import json
import smtplib
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import get_settings


def send_password_reset_email(*, recipient: str, reset_url: str) -> None:
    settings = get_settings()
    subject = "Reset your PriceYard password"
    body = (
        "We received a request to reset your PriceYard password.\n\n"
        f"Open this secure link within {settings.password_reset_expire_minutes} minutes:\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )
    send_email(recipient=recipient, subject=subject, body=body)


def send_email(*, recipient: str, subject: str, body: str) -> None:
    settings = get_settings()
    if not settings.smtp_from_email:
        raise RuntimeError("Email delivery is not configured")

    if settings.brevo_api_key:
        payload = json.dumps(
            {
                "sender": {"name": settings.smtp_from_name, "email": settings.smtp_from_email},
                "to": [{"email": recipient}],
                "subject": subject,
                "textContent": body,
            }
        ).encode("utf-8")
        request = Request(
            settings.brevo_api_url,
            data=payload,
            headers={
                "accept": "application/json",
                "api-key": settings.brevo_api_key,
                "content-type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=15) as response:
                if response.status not in {200, 201, 202}:
                    raise RuntimeError(f"Brevo email delivery failed with status {response.status}")
        except HTTPError as exc:
            raise RuntimeError(f"Brevo email delivery failed with status {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("Brevo email delivery could not reach the email provider") from exc
        return

    if not settings.smtp_host:
        raise RuntimeError("Email delivery is not configured")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = recipient
    message.set_content(body)

    context = ssl.create_default_context()
    if settings.smtp_use_ssl:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15, context=context) as server:
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        return

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.ehlo()
        if settings.smtp_use_tls:
            server.starttls(context=context)
            server.ehlo()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
