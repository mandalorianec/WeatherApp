from django.contrib.auth.password_validation import ValidationError, MinimumLengthValidator


class SimpleValidatorForTests(MinimumLengthValidator):
    def __init__(self):
        super().__init__(min_length=3)

    def validate(self, password, user=None):
        self.min_length = 3
        if len(password) < self.min_length:
            raise ValidationError(
                self.get_error_message(),
                code="password_to_short",
                params={"min_length": self.min_length}
            )
