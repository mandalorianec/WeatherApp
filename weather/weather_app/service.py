import asyncio
import logging
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError
from asyncio.exceptions import TimeoutError
from django.templatetags.static import static
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.conf import settings
from weather.users_app.models import CustomUser
from weather.weather_app.dto.weather_location_dto import WeatherLocationDto
from weather.weather_app.exceptions import ApiException, WebError, EmptySearchException, ApiAuthenticationError, \
    RateLimitExceededError

logger = logging.getLogger('main')


class OpenWeatherService:
    _geo_url = f"http://api.openweathermap.org/geo/1.0/direct?appid={settings.API_KEY}&limit=100"
    _weather_url = f"https://api.openweathermap.org/data/2.5/weather?appid={settings.API_KEY}&units=metric&lang=ru"

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def find_cities_by(self, city: str):

        try:
            response = await self._make_request(city)
            logger.info(f"GET успешный поиск, city={city}")
            return response
        except (WebError, EmptySearchException, ApiAuthenticationError, RateLimitExceededError, ApiException) as err:
            logger.warning((type(err).__name__, err.message, err.code))
            raise err
        except Exception as err:
            logger.critical(f"Непредвиденная ошибка: {(type(err).__name__, err.args[0])}")
            raise ApiException("Произошла непредвиденная ошибка")

    async def _make_request(self, city: str):
        params = {
            "q": city
        }
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with self._session.get(self._geo_url, params=params, timeout=timeout) as response:
                response.raise_for_status()
                r = await response.json()
                return r

        except (ClientConnectorError, TimeoutError) as err:
            logger.warning(f"Сетевая ошибка: {err}, city={city}")
            raise WebError()

        except ClientResponseError as err:
            status_code = err.status
            logger.warning(f"API вернул ошибку: {status_code}, city={city}")
            if status_code == 400:
                raise EmptySearchException()
            if status_code == 401:
                raise ApiAuthenticationError()
            if status_code == 429:
                raise RateLimitExceededError()
            raise ApiException(f"Неожиданный ответ от API, city={city}", code=status_code)

        except aiohttp.ClientError as err:
            logger.error(f"Общая ошибка клиента aiohttp: {err}, city={city}")
            raise ApiException()

    async def get_weather_for(self, locations: list):
        tasks = []

        for location in locations:
            url = f"{self._weather_url}&lat={location.latitude}&lon={location.longitude}"
            tasks.append(asyncio.create_task(self._fetch_one(url)))
        results = await asyncio.gather(*tasks)
        return results

    async def _fetch_one(self, url: str):
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Ошибка при обновлении погоды: {response.status}")
                    return {"cod": response.status, "message": "API error"}
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            logger.error(f"Ошибка сети при обновлении {url}: {err}")
            return {"cod": 500, "message": "Network error"}

    @staticmethod
    def get_icon_by(code: str):
        return static(f"weather_app/img/weather/{code}.png")

class WeatherService:
    def __init__(self, search_service: OpenWeatherService):
        self.search_service = search_service

    async def get_locations_for(self, user_id: int) -> list[WeatherLocationDto]:

        res = []

        user = await sync_to_async(CustomUser.objects.prefetch_related('locations').filter(pk=user_id).first)()
        user_locations = await sync_to_async(list)(user.locations.all())

        uncached_locations = []

        for location in user_locations:
            key = f"{location.latitude}:{location.longitude}"
            weather_data = cache.get(key)
            if weather_data:
                if weather_data.get('cod') != 200:
                    logger.warning(f"Локация {location.name} временно недоступна")
                    continue

                dto = self._make_weather_location_dto(location, weather_data)
                res.append(dto)
            else:
                uncached_locations.append(location)

        # Обработка некэшированных объектов
        weather_for_locations = await self.search_service.get_weather_for(uncached_locations)
        for location, weather_data in zip(uncached_locations, weather_for_locations):
            key = f"{location.latitude}:{location.longitude}"
            cache.set(key, weather_data, timeout=600)
            if weather_data.get('cod') != 200:
                logger.warning(f"Локация {location.name} временно недоступна")
                continue
            dto = self._make_weather_location_dto(location, weather_data)
            res.append(dto)
        return res

    def _make_weather_location_dto(self, location, weather_data):
        weather_translations = {
            'Clear': 'Ясно',
            'Clouds': 'Облачно',
            'Rain': 'Дождь',
            'Drizzle': 'Морось',
            'Thunderstorm': 'Гроза',
            'Snow': 'Снег',
            'Mist': 'Дымка',
            'Smoke': 'Дым',
            'Haze': 'Мгла',
            'Dust': 'Пыль',
            'Fog': 'Туман',
            'Sand': 'Песок',
            'Ash': 'Пепел',
            'Squall': 'Шквал',
            'Tornado': 'Торнадо',
        }
        weather_main_english = weather_data['weather'][0]['main']
        weather_main_russian = weather_translations.get(weather_main_english, weather_main_english)
        dto = WeatherLocationDto(
            location.pk,
            location.name,
            weather_data['sys']['country'],
            weather_main_russian,
            weather_data['weather'][0]['description'],
            weather_data['main']['temp'],
            self.search_service.get_icon_by(weather_data['weather'][0]['icon']),
            weather_data['coord']['lat'],
            weather_data['coord']['lon']
        )
        return dto
