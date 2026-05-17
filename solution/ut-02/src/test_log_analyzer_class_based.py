import pytest
from log_analyzer import LogAnalyzer

class TestLogAnalyzer:
    
    def setup_method(self):
        self.analyzer = LogAnalyzer()
        
    def test_is_valid_log_file_name_log_extension_returns_true(self):
        result = self.analyzer.is_valid_log_file_name("system.log")
        assert result is True

    def test_is_valid_log_file_name_txt_extension_returns_false(self):
        result = self.analyzer.is_valid_log_file_name("log.txt")
        assert result is False
        
    def test_is_valid_log_file_name_no_extension_returns_false(self):
        result = self.analyzer.is_valid_log_file_name("log")
        assert result is False
        
    def test_is_valid_log_file_name_log_extension_uppercase_returns_false(self):
        result = self.analyzer.is_valid_log_file_name("system.LOG")
        assert result is False

    def test_is_valid_log_file_name_multiple_dots_extension_returns_false(self):
        result = self.analyzer.is_valid_log_file_name("sys.log.txt")
        assert result is False

    def test_is_valid_log_file_name_empty_filename_raises_value_error(self):
        with pytest.raises(ValueError):
            self.analyzer.is_valid_log_file_name("")
    
    def teardown_method(self, method: pytest.Function) -> None:
        print(f"\n[teardown] finished: {method.__name__}")