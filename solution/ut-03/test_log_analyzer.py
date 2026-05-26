import pytest
from log_analyzer import LogAnalyzer

class StubExtensionManager:
    """Always reports .log and .txt as valid — no filesystem involved."""
    def get_managed_extension_list(self) -> list[str]:
        return [".log", ".txt"]

@pytest.fixture
def analyzer():
    return LogAnalyzer(manager=StubExtensionManager())


def test_is_valid_log_file_name_log_extension_returns_true(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("system.log")
    assert result is True


def test_is_valid_log_file_name_txt_extension_returns_true(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("report.txt")
    assert result is True


def test_is_valid_log_file_name_xml_extension_returns_false(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("config.xml")
    assert result is False
