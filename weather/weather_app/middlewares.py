import logging
from django.shortcuts import render

from weather.weather_app.exceptions import ApiException

logger = logging.getLogger('main')


class WeatherAppExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, ApiException):
            return render(request, 'error.html',
                          {'message': f'Ошибка {exception.code}: {exception.message}'},
                          status=exception.code
                          )
        return None
