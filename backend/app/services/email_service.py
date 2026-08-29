from email.message import EmailMessage
import smtplib
import ssl

from app.config import get_settings


def send_password_reset_email(*, recipient: str, reset_url: str) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_from_email:
        raise RuntimeError("Password reset email is not configured")

    message = EmailMessage()
    message["Subject"] = "Reset your PriceYard password"
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = recipient
    message.set_content(
        "We received a request to reset your PriceYard password.\n\n"
        f"Open this secure link within {settings.password_reset_expire_minutes} minutes:\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

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
