from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User
from wallet.models import Wallet


test_email = 'test@test.test'
test_password = 'Secret!1'  # noqa: S105 для тестов можно


class DepositTestCase(TestCase):
    """
    Тесты на /wallet/deposit/.

    Часть кейсов покрывают тесты из tests/transaction.py, дублироваться здесь они не будут.
    """

    def setUp(self):
        """Настройка тестов."""
        self.user_1 = User.objects.create_user(
            email=test_email,
            password=test_password,
        )
        self.wallet_1 = Wallet.objects.create(
            user=self.user_1,
        )
        self.user_2 = User.objects.create_user(
            email=f'{test_email}_2',
            password=f'{test_password}_2',
        )
        self.wallet_2 = Wallet.objects.create(
            user=self.user_2,
        )

    def _get_access_token(self, client: APIClient) -> str:
        response = client.post(
            path='/auth/login/',
            data={
                'email': test_email,
                'password': test_password,
            },
        )
        return response.json()['access']

    def test_bad_request_deposit(self):
        """Проверка валидации."""
        client = APIClient()
        access_token = self._get_access_token(client=client)
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token,
        )

        # неверная сумма и значение принимающего кошелька
        response = client.post(
            path='/wallet/deposit/',
            data={
                'payee': 'w',
                'amount': -1,
            },
        )
        self.assertIn('amount', response.json())
        self.assertIn('payee', response.json())
        self.assertNotIn('sender', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # несуществующий кошелёк
        response = client.post(
            path='/wallet/deposit/',
            data={
                'payee': 55,
                'amount': 100,
            },
        )
        self.assertNotIn('sender', response.json())
        self.assertNotIn('amount', response.json())
        self.assertIn('payee', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_good_deposit(self):
        """Проверка успешного пополнения."""
        client = APIClient()
        access_token = self._get_access_token(client=client)
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token,
        )

        self.assertEqual(
            Wallet.objects.get(
                pk=self.wallet_1.pk,
            ).balance,
            0,
        )

        # проверяем апи пополнения кошелька
        deposit_amount = 200
        response = client.post(
            path='/wallet/deposit/',
            data={
                'payee': self.wallet_1.pk,
                'amount': deposit_amount,
            },
        )
        self.assertNotIn('error', response.json())
        self.assertEqual(response.json(), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # проверяем, что поле balance первого и второго кошельков теперь имеют верные суммы
        self.assertEqual(
            Wallet.objects.get(
                pk=self.wallet_1.pk,
            ).balance,
            deposit_amount,
        )
