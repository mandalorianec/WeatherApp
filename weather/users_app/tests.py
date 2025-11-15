import logging
import time
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.urls import reverse

from weather.users_app.forms import SignUpForm
from weather.users_app.models import CustomUser

logger = logging.getLogger('main')

class SignUpTests(TestCase):
    @classmethod
    def setUpTestData(cls): # вызывается один раз
        CustomUser.objects.create_user('Niko', 'notfree@gmail.com', 'MyPass123!')
        CustomUser.objects.create_user('NoPass', 'newfree@gmail.com')

    def setUp(self): # вызывается перед каждым тестом
        self.username = "mika"
        self.email = "gogo@gmail.com"
        self.password = "MyPass123!"

    def test_signup_page(self):
        response = self.client.get("/signup")
        self.assertEqual(response.status_code, 301)
        self.assertTemplateUsed("signup.html")

    def test_signup_form(self):
        response = self.client.post(reverse('users:signup'), data={
            "username": self.username,
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(username=self.username).exists())

    def test_unique_username(self):
        form = SignUpForm({"username": "Niko",
                           "email": "new@gmail.com",
                           "password1": self.password,
                           "password2": self.password, })
        self.assertFalse(form.is_valid())

    def test_session_creation(self):
        self.client.cookies.clear()

        self.client.post(reverse('users:signup'), data={
            "username": self.username,
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        })

        self.assertIn("sessionid", self.client.cookies)
        self.assertNotEqual(self.client.cookies['sessionid'].value, '')

        # проверка на наличие в бд
        user_session = self.client.cookies['sessionid'].value
        self.assertTrue(Session.objects.filter(session_key=user_session).exists())

    def test_time_session(self):
        self.client.cookies.clear()

        self.client.post(reverse('users:signup'), data={
            "username": self.username,
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        })
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        time.sleep(5)
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 302)
