import pytest
from log_analyzer import ADMIN_EMAIL, LogAnalyzer
from email_service import EmailService

class StubExtensionManager:
    def get_managed_extension_list(self) -> list[str]:
        return [".log"]

class StubWebServiceThatFails:
    """Simulates a web service outage — always raises."""

    def log_error(self, message: str) -> None:
        raise ConnectionError("Web service is unreachable")


class MockEmailService:
    """Records whether send_email was called and with which arguments."""

    def __init__(self):
        self.was_called = False
        self.last_to: str | None = None
        self.last_subject: str | None = None
        self.last_body: str | None = None

    def send_email(self, to: str, subject: str, body: str) -> None:
        self.was_called = True
        self.last_to = to
        self.last_subject = subject
        self.last_body = body
        
@pytest.fixture
def mock_email():
    return MockEmailService()


@pytest.fixture
def analyzer_with_failing_service(mock_email: EmailService):
    return LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=StubWebServiceThatFails(),  # stub
        email_service=mock_email,               # mock
    )


def test_analyze_sends_email_when_web_service_fails(
    analyzer_with_failing_service: LogAnalyzer, mock_email: MockEmailService
):
    analyzer_with_failing_service.analyze("report.xml")

    assert mock_email.was_called is True


def test_analyze_email_is_sent_to_admin(
    analyzer_with_failing_service: LogAnalyzer, mock_email: MockEmailService
):
    analyzer_with_failing_service.analyze("report.xml")

    assert mock_email.last_to == ADMIN_EMAIL


def test_analyze_email_body_contains_error_reason(
    analyzer_with_failing_service: LogAnalyzer, mock_email: MockEmailService
):
    analyzer_with_failing_service.analyze("report.xml")
    
    if(mock_email.last_body is None):
        pytest.fail("Expected send_email to be called with a body, but it was not called.")

    assert "unreachable" in mock_email.last_body.lower()


def test_analyze_does_not_send_email_when_web_service_succeeds(mock_email: MockEmailService):
    class StubWebServiceThatSucceeds:
        def log_error(self, message: str) -> None:
            pass  # succeeds silently

    analyzer = LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=StubWebServiceThatSucceeds(),
        email_service=mock_email,
    )

    analyzer.analyze("report.xml")

    assert mock_email.was_called is False


def test_analyze_does_not_send_email_for_valid_file(mock_email: MockEmailService):
    class StubWebServiceThatSucceeds:
        def log_error(self, message: str) -> None:
            pass

    analyzer = LogAnalyzer(
        manager=StubExtensionManager(),
        web_service=StubWebServiceThatSucceeds(),
        email_service=mock_email,
    )

    analyzer.analyze("system.log")

    assert mock_email.was_called is False