import logging

import aiohttp
from asgiref.sync import async_to_sync
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, CreateView, View
from weather.weather_app.forms import LocationForm
from weather.weather_app.models import Location
from weather.weather_app.service import OpenWeatherService, WeatherService

# Create your views here.
logger = logging.getLogger('main')


async def _get_locations_for_(user_id: int):
    async with aiohttp.ClientSession() as session:
        search_service = OpenWeatherService(session)
        weather_service = WeatherService()
        locations = await weather_service.get_locations_for(user_id, search_service)
        return locations


class ShowLocationsView(LoginRequiredMixin, ListView):
    """Отображает добавленные локации"""
    model = Location
    template_name = 'weather/index.html'
    context_object_name = 'locations'

    paginate_by = 6

    def get_queryset(self):
        locations = async_to_sync(_get_locations_for_)(self.request.user.id)
        return locations


class AddLocationView(LoginRequiredMixin, CreateView):
    """Добавляет новую локацию по body параметрам"""
    model = Location
    success_url = reverse_lazy('home')
    form_class = LocationForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(form.errors)
        return redirect('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


async def _find_cities_with_session(city: str):
    async with aiohttp.ClientSession() as session:
        service = OpenWeatherService(session)
        return await service.find_cities_by(city)


class SearchView(LoginRequiredMixin, View):
    """Выполняет поиск локаций по параметрам"""

    def get(self, request):
        city = request.GET.get("city", "")
        if len(city) > 100:
            return render(request, 'error.html', {'status_code': 400, 'message': 'Слишком большое название'}, status=400)

        api_response = async_to_sync(_find_cities_with_session)(city)

        unique_locations = self.get_unique_locations(api_response)
        return render(request, 'weather/results.html', {"data": unique_locations})

    @staticmethod
    def get_unique_locations(api_response: list):
        used_states = set()
        res = []
        for location in api_response:
            lat_digit = int(location['lat'])
            lon_digit = int(location['lon'])
            if (lat_digit, lon_digit) in used_states:
                continue
            used_states.add((lat_digit, lon_digit))
            res.append(location)
        return res


class DeleteLocationView(LoginRequiredMixin, DeleteView):
    """Удаляет локацию по её id в бд"""
    model = Location
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        return redirect('home')  # Отключаем подтверждение удаления

    def get_queryset(self):
        return Location.objects.filter(user=self.request.user)


def error_404(request, exception):
    return render(request, 'error.html', {'status_code': 404, 'message': 'Страница не найдена'}, status=404)

def error_500(request):
    return render(request, 'error.html', {'status_code': 500, 'message': 'Внутренняя ошибка сервера'}, status=500)