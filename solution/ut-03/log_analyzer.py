from extension_manager import ExtensionManager

class LogAnalyzer:
    def __init__(self, manager: ExtensionManager):
        self._manager = manager

    def is_valid_log_file_name(self, filename: str) -> bool:
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        extension = filename[filename.rfind("."):]
        return extension in self._manager.get_managed_extension_list()