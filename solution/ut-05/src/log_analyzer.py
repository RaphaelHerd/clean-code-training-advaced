from extension_manager import ExtensionManager
from web_service import WebService

class LogAnalyzer:
    def __init__(self, manager: ExtensionManager, web_service: WebService):
        self._manager = manager
        self._web_service = web_service

    def analyze(self, filename: str) -> None:
        """Analyze a filename. Notify the web service if the extension is invalid."""
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        if extension not in self._manager.get_managed_extension_list():
            self._web_service.log_error(f"Invalid log file detected: {filename}")
