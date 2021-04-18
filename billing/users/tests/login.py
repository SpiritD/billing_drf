from django.test import TestCase
from rest_framework import status

from users.models import User
from django.test import Client


test_email = 'test@test.test'
test_password = 'Secret!1'


class LoginTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(
            email=test_email,
            password=test_password,
        )

    def test_bad_request(self):
        """Проверка валидации."""
        client = Client()
        # неверный пароль
        response = client.post(
            path='/auth/login/',
            data={
                'email': test_email,
                'password': 'secret',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # неверное имя параметра у пароля
        response = client.post(
            path='/auth/login/',
            data={
                'email': test_email,
                'password2': test_password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auth(self):
        """Проверка авторизации."""
        client = Client()
        response = client.post(
            path='/auth/login/',
            data={
                'email': test_email,
                'password': test_password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # проверяем, что вернулись токены
        self.assertIn('refresh', response.json())
        self.assertIn('access', response.json())

    def test_refresh_token(self):
        """
        Проверка обновление пары ключей.

        Обязательно проверяем, что при "протухании" access токена пользователю не надо будет
        авторизовываться каждый раз.
        """
        client = Client()
        response = client.post(
            path='/auth/login/',
            data={
                'email': test_email,
                'password': test_password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # проверяем, что вернулись токены
        self.assertIn('refresh', response.json())
        self.assertIn('access', response.json())
        refresh_token = response.json()['refresh']
        access_token = response.json()['access']

        response = client.post(
            path='/auth/login/refresh/',
            data={
                'refresh': refresh_token,
            },
        )
        self.assertIn('refresh', response.json())
        self.assertIn('access', response.json())
        new_refresh_token = response.json()['refresh']
        new_access_token = response.json()['access']

        # проверяем, что они отличаются от предыдущих
        self.assertNotEqual(refresh_token, new_refresh_token)
        self.assertNotEqual(access_token, new_access_token)
