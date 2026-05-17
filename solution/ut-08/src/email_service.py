from typing import Protocol

class EmailService(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> None:
        ...


class SmtpEmailService:
    """Production implementation — sends a real email via SMTP."""

    def send_email(self, to: str, subject: str, body: str) -> None:
        raise NotImplementedError("Not used in tests")