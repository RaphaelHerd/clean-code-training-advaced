import pytest
from log_analyzer import LogAnalyzer

def test_is_valid_log_file_name_log_extension_returns_true():
    # Arrange
    analyzer = LogAnalyzer()

    # Act
    result = analyzer.is_valid_log_file_name("system.log")

    # Assert
    assert result is True


def test_is_valid_log_file_name_txt_extension_returns_false():
    # Arrange
    analyzer = LogAnalyzer()

    # Act
    result = analyzer.is_valid_log_file_name("log.txt")

    # Assert
    assert result is False
    
def test_is_valid_log_file_name_no_extension_returns_false():
    # Arrange
    analyzer = LogAnalyzer()

    # Act
    result = analyzer.is_valid_log_file_name("log")

    # Assert
    assert result is False
    
def test_is_valid_log_file_name_log_extension_uppercase_returns_false():
    # Arrange
    analyzer = LogAnalyzer()

    # Act
    result = analyzer.is_valid_log_file_name("system.LOG")

    # Assert
    assert result is False

def test_is_valid_log_file_name_multiple_dots_extension_returns_false():
    # Arrange
    analyzer = LogAnalyzer()

    # Act
    result = analyzer.is_valid_log_file_name("sys.log.txt")

    # Assert
    assert result is False

def test_is_valid_log_file_name_empty_filename_raises_value_error():
    # Arrange
    analyzer = LogAnalyzer()

    # Act / Assert
    with pytest.raises(ValueError):
        analyzer.is_valid_log_file_name("")