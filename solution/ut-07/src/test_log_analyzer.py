import pytest
from unittest.mock import MagicMock
from log_analyzer import ADMIN_EMAIL, LogAnalyzer

class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]


@pytest.fixture
def web_service_mock():
    return MagicMock()

@pytest.fixture
def email_mock():
    return MagicMock()


@pytest.fixture
def analyzer(web_service_mock: MagicMock):
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=web_service_mock,
        email_service=MagicMock(),  # not the focus of these tests → stub role
    )

@pytest.fixture
def analyzer_with_failing_service(email_mock: MagicMock):
    failing_web_service = MagicMock()
    failing_web_service.log_error.side_effect = ConnectionError("unreachable")
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=failing_web_service,   # stub via side_effect
        email_service=email_mock,          # mock
    )

def test_analyze_invalid_extension_calls_log_error(analyzer: LogAnalyzer, web_service_mock: MagicMock):
    analyzer.analyze("report.xml")
    web_service_mock.log_error.assert_called_once()


def test_analyze_invalid_extension_sends_filename_in_message(analyzer: LogAnalyzer, web_service_mock: MagicMock):
    analyzer.analyze("report.xml")
    args = web_service_mock.log_error.call_args.args
    assert "report.xml" in args[0]


def test_analyze_valid_extension_does_not_call_log_error(analyzer: LogAnalyzer, web_service_mock: MagicMock):
    analyzer.analyze("system.log")
    web_service_mock.log_error.assert_not_called()
    
def test_sends_email_when_web_service_fails(analyzer_with_failing_service: LogAnalyzer, email_mock: MagicMock):
    analyzer_with_failing_service.analyze("report.xml")

    email_mock.send_email.assert_called_once()


def test_email_is_sent_to_admin(analyzer_with_failing_service: LogAnalyzer, email_mock: MagicMock):
    analyzer_with_failing_service.analyze("report.xml")

    _, kwargs = email_mock.send_email.call_args
    assert kwargs["to"] == ADMIN_EMAIL


def test_no_email_when_web_service_succeeds(email_mock: MagicMock):
    working_service = MagicMock()  # does not raise
    analyzer = LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=working_service,
        email_service=email_mock,
    )

    analyzer.analyze("report.xml")

    email_mock.send_email.assert_not_called()