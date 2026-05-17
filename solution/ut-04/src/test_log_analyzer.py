import pytest
from log_analyzer import LogAnalyzer

class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]

class StubLogger:
    def __init__(self):
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)

@pytest.fixture
def analyzer():
    return LogAnalyzer(manager=StubExtensionManager())

# --- Constructor injection ---

def test_constructor_requires_manager():
    with pytest.raises(TypeError):
        LogAnalyzer() # type: ignore


def test_valid_file_returns_true_without_custom_logger(analyzer: LogAnalyzer):
    # No logger injected — NullLogger is used transparently
    result = analyzer.is_valid_log_file_name("system.log")
    assert result is True


# --- Property injection ---

def test_logger_receives_message_when_valid_file_checked(analyzer: LogAnalyzer):
    stub_logger = StubLogger()
    analyzer.logger = stub_logger  # property injection

    analyzer.is_valid_log_file_name("system.log")

    assert len(stub_logger.messages) == 1
    assert "system.log" in stub_logger.messages[0]


def test_logger_message_contains_invalid_when_extension_unknown(analyzer: LogAnalyzer):
    stub_logger = StubLogger()
    analyzer.logger = stub_logger

    analyzer.is_valid_log_file_name("report.csv")

    assert "invalid" in stub_logger.messages[0]