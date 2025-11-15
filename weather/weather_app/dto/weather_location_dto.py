from dataclasses import dataclass


@dataclass
class WeatherLocationDto:
    """DTO карточки одной локации на главной странице"""
    id: int
    city: str
    country: str
    weather: str
    description: str
    temp: float
    icon_url: str
    lat: str
    lon: str
