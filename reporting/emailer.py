"""
reporting/emailer.py
----------------------
Sends the generated .docx report as an email attachment via SMTP
(STARTTLS). Stateless — takes an EmailConfig and a file path, does one
thing.
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from core.config import EmailConfig

log = logging.getLogger(__name__)


def send_report_email(email_cfg: EmailConfig, attachment_path: str | Path, body: str) -> None:
    """
    Sends attachment_path as an email to every address in email_cfg.to_email.

    Raises
    ------
    smtplib.SMTPException  On any SMTP-level failure (auth, connection, etc).
    """
    attachment_path = Path(attachment_path)

    msg = MIMEMultipart()
    msg["From"] = email_cfg.from_email
    msg["To"] = ", ".join(email_cfg.to_email)
    msg["Subject"] = email_cfg.subject
    msg.attach(MIMEText(body, "plain"))

    with attachment_path.open("rb") as fh:
        part = MIMEApplication(fh.read(), Name=attachment_path.name)
    part["Content-Disposition"] = f'attachment; filename="{attachment_path.name}"'
    msg.attach(part)

    log.info(
        "Sending report email: server=%s:%d from=%s to=%s subject=%r",
        email_cfg.smtp_server, email_cfg.smtp_port, email_cfg.from_email,
        email_cfg.to_email, email_cfg.subject,
    )

    with smtplib.SMTP(email_cfg.smtp_server, email_cfg.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(email_cfg.smtp_user, email_cfg.smtp_password)
        smtp.sendmail(email_cfg.from_email, list(email_cfg.to_email), msg.as_string())

    log.info("Report email sent successfully")
