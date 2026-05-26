from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class PasswordValidator:
    SPECIAL_CHARS = set("!@#$%^&*")
    
    def validate(self, password: str) -> ValidationResult:
        errors = list[str]()
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c in self.SPECIAL_CHARS for c in password):
            errors.append("Password must contain at least one special character (!@#$%^&*)")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)