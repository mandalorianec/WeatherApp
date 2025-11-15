from django.urls import path

from weather.weather_app.views import SearchView, DeleteLocationView, AddLocationView

app_name = 'weather'

urlpatterns = [
    path('search/', SearchView.as_view(), name='search'),
    path('location/delete/<int:pk>/', DeleteLocationView.as_view(), name='delete'),
    path('location/add/', AddLocationView.as_view(), name='add'),
]
