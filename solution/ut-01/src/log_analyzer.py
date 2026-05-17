class LogAnalyzer:
    VALID_EXTENSIONS = [".log"]

    def is_valid_log_file_name(self, filename: str) -> bool:
        """Return True when the file's extension is in the allowed list."""
        if not filename:
            raise ValueError("Filename cannot be empty")
        extension = filename[filename.rfind("."):]
        return extension in self.VALID_EXTENSIONS