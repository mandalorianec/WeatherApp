from django.core.exceptions import ValidationError


class SimplePasswordLengthValidator:
    def __init__(self, min_length=3, max_length=30):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) < self.min_length or len(password) > self.max_length:
            raise ValidationError(
                f"Пароль должен содержать от {self.min_length} до {self.max_length} символов.",
                code="invalid_length",
            )

    def get_help_text(self):
        return f"Пароль должен содержать от {self.min_length} до {self.max_length} символов."