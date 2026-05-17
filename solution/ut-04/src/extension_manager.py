from typing import Protocol

class ExtensionManager(Protocol):
    def get_managed_extension_list(self) -> list[str]: ...


class FileExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        with open("extensions.txt") as f:
            return [line.strip() for line in f if line.strip()]