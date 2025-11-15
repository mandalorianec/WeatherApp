from django.contrib.auth.views import LogoutView
from django.urls import path

from weather.users_app.views import LoginUser, SignUpUser

app_name = 'users'

urlpatterns = [
    path('signup/', SignUpUser.as_view(), name="signup"),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
]