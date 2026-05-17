import pytest
from unittest.mock import MagicMock, create_autospec
from web_service import WebService

def test_strict_mock_rejects_typo():
    mock = MagicMock(spec=WebService)

    with pytest.raises(AttributeError):
        mock.log_errror("oops")   # raises — method does not exist on WebService


def test_autospec_validates_argument_count():
    mock = create_autospec(WebService)

    with pytest.raises(TypeError):
        mock.log_error("first", "unexpected_second_arg")  # too many arguments


def test_strict_mock_fails_when_expected_call_is_missing():
    mock = MagicMock(spec=WebService)
    # Don't call mock.log_error at all

    with pytest.raises(AssertionError):
        mock.log_error.assert_called_once()


def test_strict_mock_fails_when_unexpected_method_is_called():
    mock = MagicMock(spec=WebService)

    with pytest.raises(AttributeError):
        mock.nonexistent_method()