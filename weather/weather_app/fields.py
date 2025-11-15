import logging

from django import forms

logger = logging.getLogger('main')

class CommaDecimalField(forms.DecimalField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, str):
            value = value.replace(',', '.')
        value = round(float(value), 9)
        return super().to_python(value)
