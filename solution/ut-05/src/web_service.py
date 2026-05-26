from typing import Protocol

class WebService(Protocol):
    def log_error(self, message: str) -> None: ...

class RealWebService:
    """Production implementation — calls an actual HTTP endpoint."""

    def log_error(self, message: str) -> None:
        # In production this would POST to an API endpoint.
        raise NotImplementedError("Not used in tests")