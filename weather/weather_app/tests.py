from unittest.mock import AsyncMock, Mock, MagicMock
from asgiref.sync import async_to_sync
from django.test import TestCase

from weather.weather_app.dto.weather_location_dto import WeatherLocationDto
from weather.weather_app.exceptions import WebError
from weather.weather_app.service import WeatherService
from weather.users_app.models import CustomUser
from weather.weather_app.models import Location
from weather.weather_app.service import OpenWeatherService


# Create your tests here.
class ServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Создаем локации для пользователя
        cls.location1 = Location.objects.create(
            name='Berlin', # классический Берлин - столица Германии
            latitude=52.517036500,
            longitude=13.388859900,
            user=cls.user
        )

        cls.location2 = Location.objects.create(
            name='London',
            latitude=51.507321900,
            longitude=-0.127647400,
            user=cls.user
        )

        cls.location3 = Location.objects.create(
            name='Vienna',
            latitude=48.208353700,
            longitude=16.372504200,
            user=cls.user
        )

        cls.location4 = Location.objects.create(
            name='Prague',
            latitude=50.087465400,
            longitude=14.421253500,
            user=cls.user
        )

        # Подготовленные данные - имитация ответа API
        cls.test_data = [
            {'base': 'stations', 'clouds': {'all': 40}, 'cod': 200, 'coord': {'lat': 52.517, 'lon': 13.3889},
             'dt': 1762801683, 'id': 7576815,
             'main': {'feels_like': 7.91, 'grnd_level': 1009, 'humidity': 90, 'pressure': 1015, 'sea_level': 1015,
                      'temp': 8.31, 'temp_max': 8.94, 'temp_min': 6.67}, 'name': 'Alt-Kölln', # Это часть столицы Германии, часть Берлина
             'sys': {'country': 'DE', 'id': 2011538, 'sunrise': 1762755558, 'sunset': 1762788092, 'type': 2},
             'timezone': 3600, 'visibility': 10000,
             'weather': [{'description': 'scattered clouds', 'icon': '03n', 'id': 802, 'main': 'Clouds'}],
             'wind': {'deg': 250, 'speed': 1.34}},

            {'base': 'stations', 'clouds': {'all': 75}, 'cod': 200, 'coord': {'lat': 51.5073, 'lon': -0.1276},
             'dt': 1762795171, 'id': 2643743,
             'main': {'feels_like': 10.81, 'grnd_level': 999, 'humidity': 92, 'pressure': 1003, 'sea_level': 1003,
                      'temp': 11.23, 'temp_max': 11.86, 'temp_min': 10.51}, 'name': 'London',
             'sys': {'country': 'GB', 'id': 2075535, 'sunrise': 1762758601, 'sunset': 1762791536, 'type': 2},
             'timezone': 0, 'visibility': 10000,
             'weather': [{'description': 'light rain', 'icon': '10n', 'id': 500, 'main': 'Rain'}],
             'wind': {'deg': 220, 'speed': 4.12}},

            {'base': 'stations', 'clouds': {'all': 20}, 'cod': 200, 'coord': {'lat': 48.2084, 'lon': 16.3725},
             'dt': 1762795383, 'id': 2761369,
             'main': {'feels_like': 8.37, 'grnd_level': 989, 'humidity': 84, 'pressure': 1016, 'sea_level': 1016,
                      'temp': 8.92, 'temp_max': 9.93, 'temp_min': 6.96}, 'name': 'Vienna',
             'sys': {'country': 'AT', 'id': 2037452, 'sunrise': 1762754032, 'sunset': 1762788186, 'type': 2},
             'timezone': 3600, 'visibility': 10000,
             'weather': [{'description': 'few clouds', 'icon': '02n', 'id': 801, 'main': 'Clouds'}],
             'wind': {'deg': 90, 'speed': 1.54}},

            {'base': 'stations', 'clouds': {'all': 0}, 'cod': 200, 'coord': {'lat': 50.0851, 'lon': 14.4248},
             'dt': 1762795510, 'id': 3067696,
             'main': {'feels_like': 6.45, 'grnd_level': 981, 'humidity': 90, 'pressure': 1016, 'sea_level': 1016,
                      'temp': 8.35, 'temp_max': 9.03, 'temp_min': 7.53}, 'name': 'Prague',
             'sys': {'country': 'CZ', 'id': 2010430, 'sunrise': 1762754833, 'sunset': 1762788320, 'type': 2},
             'timezone': 3600, 'visibility': 10000,
             'weather': [{'description': 'clear sky', 'icon': '01n', 'id': 800, 'main': 'Clear'}],
             'wind': {'deg': 190, 'speed': 3.13}}
        ]


    def test_locations_for_user(self):
        """Проверка на формирование dto с погодой для главной страницы"""
        service_mock = Mock(spec_set=OpenWeatherService)
        service_mock.get_weather_for.return_value = self.test_data
        service_mock.get_icon_by.return_value = "https://openweathermap.org/img/wn/04n@2x.png" # просто для теста

        weather_service = WeatherService()

        locations = async_to_sync(weather_service.get_locations_for)(self.user.pk, service_mock)

        self.assertEqual(len(locations), 4)

        for dto in locations:
            self.assertIsInstance(dto, WeatherLocationDto)

        service_mock.get_weather_for.assert_called_once()

        # проверка конкретных значений
        berlin_dto = locations[0]
        self.assertEqual(berlin_dto.id, self.location1.pk)
        self.assertEqual(berlin_dto.city, 'Berlin')  # api иногда возвращает другое название(Alt-Kölln - Часть Берлина)
        self.assertEqual(berlin_dto.weather, 'Clouds')
        self.assertEqual(berlin_dto.description, 'scattered clouds')
        self.assertEqual(berlin_dto.temp, 8.31)

        required_fields = ['id', 'city', 'weather', 'description', 'temp', 'icon_url', 'lat', 'lon']
        for dto in locations:
            for field in required_fields:
                self.assertTrue(hasattr(dto, field))


class SearchServiceTests(TestCase):
    def test_cities_search(self):
        """Проверка на формирование ответа в поиске"""
        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=[
            {'country': 'US', 'lat': 33.6617962, 'lon': -95.555513, 'name': 'Paris', 'state': 'Texas'},
            {'country': 'US', 'lat': 38.2097987, 'lon': -84.2529869, 'name': 'Paris', 'state': 'Kentucky'},
            {'country': 'FR', 'lat': 48.8588897,
             'local_names': {'af': 'Parys', 'am': 'ፓሪስ', 'an': 'París', 'ar': 'باريس', 'ba': 'Париж', 'be': 'Парыж',
                             'bg': 'Париж', 'bn': 'প্যারিস', 'bo': 'ཕ་རི།', 'br': 'Pariz', 'bs': 'Pariz', 'ca': 'París',
                             'co': 'Parighji', 'cs': 'Paříž', 'cu': 'Парижь', 'cv': 'Парис', 'de': 'Paris',
                             'el': 'Παρίσι', 'eo': 'Parizo', 'es': 'París', 'et': 'Pariis', 'eu': 'Paris',
                             'fa': 'پاریس', 'fi': 'Pariisi', 'fr': 'Paris', 'fy': 'Parys', 'ga': 'Páras', 'gl': 'París',
                             'gn': 'Parĩ', 'gu': 'પૅરિસ', 'gv': 'Paarys', 'ha': 'Pariis', 'he': 'פריז', 'hi': 'पैरिस',
                             'hr': 'Pariz', 'ht': 'Pari', 'hu': 'Párizs', 'hy': 'Փարիզ', 'is': 'París', 'it': 'Parigi',
                             'ja': 'パリ', 'ka': 'პარიზი', 'kk': 'Париж', 'km': 'ប៉ារីស', 'kn': 'ಪ್ಯಾರಿಸ್', 'ko': '파리',
                             'ku': 'Parîs', 'kv': 'Париж', 'ky': 'Париж', 'la': 'Lutetia', 'lb': 'Paräis',
                             'li': 'Paries', 'ln': 'Pari', 'lt': 'Paryžius', 'lv': 'Parīze', 'mi': 'Parī',
                             'mk': 'Париз', 'ml': 'പാരിസ്', 'mn': 'Парис', 'mr': 'पॅरिस', 'my': 'ပါရီမြို့',
                             'ne': 'पेरिस', 'nl': 'Parijs', 'no': 'Paris', 'oc': 'París', 'or': 'ପ୍ୟାରିସ',
                             'os': 'Париж', 'pa': 'ਪੈਰਿਸ', 'pl': 'Paryż', 'ps': 'پاريس', 'ru': 'Париж', 'sc': 'Parigi',
                             'sh': 'Pariz', 'sk': 'Paríž', 'sl': 'Pariz', 'so': 'Baariis', 'sq': 'Parisi',
                             'sr': 'Париз', 'sv': 'Paris', 'ta': 'பாரிஸ்', 'te': 'పారిస్', 'tg': 'Париж', 'th': 'ปารีส',
                             'tk': 'Pariž', 'tl': 'Paris', 'tt': 'Париж', 'ug': 'پارىژ', 'uk': 'Париж', 'ur': 'پیرس',
                             'uz': 'Parij', 'vi': 'Paris', 'wo': 'Pari', 'yi': 'פאריז', 'yo': 'Parisi', 'za': 'Bahliz',
                             'zh': '巴黎', 'zu': 'IParisi'}, 'lon': 2.3200410217200766, 'name': 'Paris',
             'state': 'Ile-de-France'},
        ])
        response_mock.raise_for_status = lambda: None
        session_mock = MagicMock()

        session_mock.get.return_value.__aenter__.return_value = response_mock
        session_mock.get.return_value.__aexit__.return_value = AsyncMock()

        service = OpenWeatherService(session_mock)

        api_response = async_to_sync(service.find_cities_by)("Berlin")

        self.assertEqual(len(api_response), 3)
        self.assertEqual(api_response[0]['name'], 'Paris')
        self.assertEqual(api_response[0]['state'], 'Texas')

    def test_network_error(self):
        """Проверка, на выбрасываемое исключение"""
        session_mock = MagicMock()

        session_mock.get.side_effect = WebError()

        service = OpenWeatherService(session_mock)

        with self.assertRaises(WebError):
            api_response = async_to_sync(service.find_cities_by)("Berlin")

