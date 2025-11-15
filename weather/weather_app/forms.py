from django import forms
from django.core.exceptions import ValidationError
from weather.weather_app.models import Location
from .fields import CommaDecimalField
from django.db.models.functions import Floor
import logging

logger = logging.getLogger('main')


class LocationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    latitude = CommaDecimalField(widget=forms.HiddenInput(), max_digits=12, decimal_places=9)
    longitude = CommaDecimalField(widget=forms.HiddenInput(), max_digits=12, decimal_places=9)

    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude']

    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data['name']
        latitude = int(cleaned_data['latitude'])
        longitude = int(cleaned_data['longitude'])
        logger.info(f"int latitude: {latitude}")
        logger.info(f"int longitude: {longitude}")

        locations_with_rounded_coords = Location.objects.annotate(
            int_lat=Floor('latitude'),
            int_lon=Floor('longitude')
        )

        if locations_with_rounded_coords.filter(user=self.user, name=name, int_lat=latitude,
                                                int_lon=longitude).exists():
            logger.info(f"Попытка добавить дубликат {name, cleaned_data['latitude'], cleaned_data['longitude']}")
            raise ValidationError("Локация уже отслеживается")
        return cleaned_data
