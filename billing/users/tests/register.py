from django.test import TestCase
from rest_framework import status

from users.models import User
from django.test import Client


class RegisterTestCase(TestCase):

    def test_bad_request(self):
        """Проверка валидации."""
        client = Client()
        # неверные параметры
        response = client.post(
            path='/auth/register/',
            data={'name': 'test', 'passwd': 'secret'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # неверная почта
        response = client.post(
            path='/auth/register/',
            data={
                'email': 'test',
                'password': 'secret',
                'password2': 'secret',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # неверные пароли
        response = client.post(
            path='/auth/register/',
            data={
                'email': 'test@test.test',
                'password': 'secret',
                'password2': 'secret2',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Пароли очень простые
        response = client.post(
            path='/auth/register/',
            data={
                'email': 'test@test.test',
                'password': 'secret',
                'password2': 'secret',
            },
        )
        self.assertIn('password', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register(self):
        """Проверка регистрации пользователя."""
        client = Client()
        test_email = 'test@test.test'
        test_password = 'Secret!1'

        response = client.post(
            path='/auth/register/',
            data={
                'email': test_email,
                'password': test_password,
                'password2': test_password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(
            email=test_email,
        )
        self.assertEqual(user.email, test_email)
        self.assertNotEqual(user.password, test_password)
        self.assertEqual(user.first_name, None)
        self.assertEqual(user.last_name, None)
        self.assertEqual(user.get_full_name(), test_email)

    def test_register_user_name(self):
        """Проверка регистрации пользователя с необязательными полями."""
        client = Client()
        test_email = 'test@test.test'
        test_password = 'Secret!1'
        # это не копипаст откуда-то, я люблю стар трек
        test_first_name = 'Scott'
        test_last_name = 'Montgomery'

        response = client.post(
            path='/auth/register/',
            data={
                'email': test_email,
                'password': test_password,
                'password2': test_password,
                'first_name': test_first_name,
                'last_name': test_last_name,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(
            email=test_email,
        )
        self.assertEqual(user.email, test_email)
        self.assertNotEqual(user.password, test_password)
        self.assertEqual(user.first_name, test_first_name)
        self.assertEqual(user.last_name, test_last_name)
        self.assertEqual(user.get_full_name(), f'{test_first_name} {test_last_name}')
