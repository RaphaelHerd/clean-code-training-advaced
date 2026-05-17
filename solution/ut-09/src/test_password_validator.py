from password_validator import PasswordValidator

def test_validate_returns_error_message_for_short_password():
    validator = PasswordValidator()
    result = validator.validate("Ab1!")
    assert any("8 characters" in e for e in result.errors)


def test_validate_returns_error_message_for_missing_uppercase():
    validator = PasswordValidator()
    result = validator.validate("abcd123!")
    assert any("uppercase" in e.lower() for e in result.errors)


def test_validate_returns_multiple_errors_when_multiple_rules_fail():
    validator = PasswordValidator()
    result = validator.validate("abc")  # too short, no uppercase, no special char
    assert len(result.errors) == 3
    
def test_password_meeting_all_rules_is_valid():
    validator = PasswordValidator()
    result = validator.validate("Abcd123!")
    assert result.is_valid is True


# Additional tests covering edge cases and boundaries

def test_password_exactly_8_characters_with_all_requirements():
    """Test boundary: exactly 8 characters with uppercase and special char"""
    validator = PasswordValidator()
    result = validator.validate("Abcdefg!")
    assert result.is_valid is True


def test_password_with_7_characters_fails_length_check():
    """Test boundary: 7 characters (one less than minimum)"""
    validator = PasswordValidator()
    result = validator.validate("Abcdef!")
    assert not result.is_valid
    assert any("8 characters" in e for e in result.errors)


def test_password_with_only_lowercase_and_numbers():
    """Test missing uppercase and special character"""
    validator = PasswordValidator()
    result = validator.validate("abcdefgh123")
    assert not result.is_valid
    assert len(result.errors) == 2
    assert any("uppercase" in e.lower() for e in result.errors)
    assert any("special character" in e.lower() for e in result.errors)


def test_password_with_uppercase_and_numbers_but_no_special_char():
    """Test missing special character requirement"""
    validator = PasswordValidator()
    result = validator.validate("Abcdefgh123")
    assert not result.is_valid
    assert len(result.errors) == 1
    assert any("special character" in e.lower() for e in result.errors)


def test_password_with_all_special_characters_no_letters():
    """Test password with only special characters"""
    validator = PasswordValidator()
    result = validator.validate("!@#$%^&*")
    assert not result.is_valid
    assert any("uppercase" in e.lower() for e in result.errors)


def test_password_with_multiple_special_characters():
    """Test valid password with multiple special characters"""
    validator = PasswordValidator()
    result = validator.validate("Abcdef!@")
    assert result.is_valid is True


def test_password_with_multiple_uppercase_letters():
    """Test valid password with multiple uppercase letters"""
    validator = PasswordValidator()
    result = validator.validate("ABCDEfgh!")
    assert result.is_valid is True


def test_empty_password():
    """Test empty password fails all validations"""
    validator = PasswordValidator()
    result = validator.validate("")
    assert not result.is_valid
    assert len(result.errors) == 3
    assert any("8 characters" in e for e in result.errors)
    assert any("uppercase" in e.lower() for e in result.errors)
    assert any("special character" in e.lower() for e in result.errors)


def test_password_with_only_spaces():
    """Test password with only spaces fails validation"""
    validator = PasswordValidator()
    result = validator.validate("        ")
    assert not result.is_valid
    assert len(result.errors) == 2  # missing uppercase and special char
    assert any("uppercase" in e.lower() for e in result.errors)
    assert any("special character" in e.lower() for e in result.errors)


def test_password_with_valid_special_char_at_start():
    """Test valid password with special character at start"""
    validator = PasswordValidator()
    result = validator.validate("!Abcdefgh")
    assert result.is_valid is True


def test_password_with_valid_special_char_at_end():
    """Test valid password with special character at end"""
    validator = PasswordValidator()
    result = validator.validate("Abcdefgh!")
    assert result.is_valid is True


def test_each_special_character_is_accepted():
    """Test that each allowed special character is recognized"""
    validator = PasswordValidator()
    special_chars = "!@#$%^&*"
    for char in special_chars:
        result = validator.validate(f"Abcdefgh{char}")
        assert result.is_valid is True, f"Special character '{char}' should be valid"


def test_password_validation_error_messages_format():
    """Test that error messages have proper formatting"""
    validator = PasswordValidator()
    result = validator.validate("abc")
    assert all(isinstance(e, str) and len(e) > 0 for e in result.errors)
    assert all("Password must" in e for e in result.errors)
    
