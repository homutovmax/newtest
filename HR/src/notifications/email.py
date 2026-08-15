"""Email notifications via SMTP (no sendmail dependency)."""
import smtplib
from email.mime.text import MIMEText
from src.config import settings


def send_digest(subject: str, html_body: str):
    try:
        msg = MIMEText(html_body, "html", "utf-8")
        msg["From"] = settings.email_from
        msg["To"] = settings.email_to
        msg["Subject"] = subject

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)

        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email error: {e}")
