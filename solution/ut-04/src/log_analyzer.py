from typing import Protocol

from extension_manager import ExtensionManager

class Logger(Protocol):
    def log(self, message: str) -> None: ...

class NullLogger:
    """Default logger that silently discards all messages."""
    def log(self, message: str) -> None:
        pass

class LogAnalyzer:
    def __init__(self, manager: ExtensionManager):
        self._manager = manager
        self._logger: Logger = NullLogger() # safe default

    @property
    def logger(self) -> Logger:
        return self._logger

    @logger.setter
    def logger(self, value: Logger) -> None:
        self._logger = value
    
    def is_valid_log_file_name(self, filename: str) -> bool:
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        valid = extension in self._manager.get_managed_extension_list()
        self._logger.log(f"Checked '{filename}': {'valid' if valid else 'invalid'}")
        return valid