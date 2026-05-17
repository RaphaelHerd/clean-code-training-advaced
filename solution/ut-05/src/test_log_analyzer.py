import pytest
from log_analyzer import LogAnalyzer

class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]


class MockWebService:
    def __init__(self):
        self.log_error_was_called = False
        self.last_error_message: str | None = None
        self.call_count = 0

    def log_error(self, message: str) -> None:
        self.log_error_was_called = True
        self.last_error_message = message
        self.call_count += 1


@pytest.fixture
def mock_service():
    return MockWebService()


@pytest.fixture
def analyzer(mock_service: MockWebService):
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=mock_service,
    )


def test_analyze_invalid_extension_calls_log_error(analyzer: LogAnalyzer, mock_service: MockWebService):
    # Act
    analyzer.analyze("report.xml")

    # Assert interaction
    assert mock_service.log_error_was_called is True


def test_analyze_invalid_extension_sends_filename_in_message(analyzer: LogAnalyzer, mock_service: MockWebService):
    analyzer.analyze("report.xml")

    if mock_service.last_error_message is None:
        pytest.fail("Expected log_error to be called with a message, but it was not called.")
    
    assert "report.xml" in mock_service.last_error_message


def test_analyze_valid_extension_does_not_call_log_error(analyzer: LogAnalyzer, mock_service: MockWebService):
    analyzer.analyze("system.log")

    assert mock_service.log_error_was_called is False


def test_analyze_invalid_extension_calls_log_error_exactly_once(analyzer: LogAnalyzer, mock_service: MockWebService):
    analyzer.analyze("report.xml")

    assert mock_service.call_count == 1
    
def test_analyze_multiple_invalid_extensions_calls_log_error_multiple_times(analyzer: LogAnalyzer, mock_service: MockWebService):
    analyzer.analyze("report.xml")
    analyzer.analyze("config.json")

    assert mock_service.call_count == 2