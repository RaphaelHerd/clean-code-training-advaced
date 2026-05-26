from extension_manager import ExtensionManager
from web_service import WebService
from email_service import EmailService

ADMIN_EMAIL = "admin@shoplog.internal"


class LogAnalyzer:
    def __init__(
        self,
        manager: ExtensionManager,
        web_service: WebService,
        email_service: EmailService,
    ):
        self._manager = manager
        self._web_service = web_service
        self._email_service = email_service

    def analyze(self, filename: str) -> None:
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        extension = filename[filename.rfind("."):]
        if extension not in self._manager.get_managed_extension_list():
            try:
                self._web_service.log_error(f"Invalid log file: {filename}")
            except Exception as e:
                self._email_service.send_email(
                    to=ADMIN_EMAIL,
                    subject="Web service unreachable",
                    body=str(e),
                )