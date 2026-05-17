import pytest
from log_analyzer import LogAnalyzer

@pytest.fixture
def analyzer():
    return LogAnalyzer()
        
def test_is_valid_log_file_name_log_extension_returns_true(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("system.log")
    assert result is True

def test_is_valid_log_file_name_txt_extension_returns_false(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("log.txt")
    assert result is False

def test_is_valid_log_file_name_no_extension_returns_false(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("log")
    assert result is False

def test_is_valid_log_file_name_log_extension_uppercase_returns_false(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("system.LOG")
    assert result is False

def test_is_valid_log_file_name_multiple_dots_extension_returns_false(analyzer: LogAnalyzer):
    result = analyzer.is_valid_log_file_name("sys.log.txt")
    assert result is False

def test_is_valid_log_file_name_empty_filename_raises_value_error(analyzer: LogAnalyzer):
    with pytest.raises(ValueError):
        analyzer.is_valid_log_file_name("")

def test_add_extension_affects_next_test_antipattern(analyzer: LogAnalyzer):
    analyzer.VALID_EXTENSIONS.append(".xml")
    result = analyzer.is_valid_log_file_name("config.xml")
    assert result is True

def test_xml_should_not_be_valid(analyzer: LogAnalyzer):
    # This should return False — but does it?
    # If the previous test ran first, it will return True (since the same LogAnalyzer reference is used), 
    # which is a test order dependency and an antipattern.
    result = analyzer.is_valid_log_file_name("config.xml")
    assert result is False
