from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User
from wallet.models import (
    Transaction,
    Wallet,
)


test_email = 'test@test.test'
test_password = 'Secret!1'  # noqa: S105 для тестов можно


class TransactionTestCase(TestCase):
    """Тесты на /wallet/transaction/ и модель Transaction."""

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

    def test_setup(self):
        """Проверка, что тесты настроились верно."""
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Wallet.objects.count(), 2)

        for wallet in Wallet.objects.all():
            self.assertEquals(wallet.balance, 0)

    def test_bad_request(self):
        """Проверка валидации."""
        client = APIClient()
        access_token = self._get_access_token(client=client)
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token,
        )

        # неверная сумма и другие значения
        response = client.post(
            path='/wallet/transaction/',
            data={
                'sender': 'q',
                'payee': 'w',
                'amount': -1,
            },
        )
        self.assertIn('amount', response.json())
        self.assertIn('payee', response.json())
        self.assertIn('sender', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # нет отправителя
        response = client.post(
            path='/wallet/transaction/',
            data={
                'payee': self.wallet_1.pk,
                'amount': 100,
            },
        )
        self.assertIn('sender', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_enough_balance(self):
        """Проверка поведения, когда не хватает баланса."""
        client = APIClient()
        access_token = self._get_access_token(client=client)
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token,
        )

        response = client.post(
            path='/wallet/transaction/',
            data={
                'sender': self.wallet_1.pk,
                'payee': self.wallet_2.pk,
                'amount': 100,
            },
        )
        self.assertIn('error', response.json())
        self.assertEqual(response.json(), {'error': 'insufficient funds'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_wallet_transactions_sum(self):
        """Тестируем метод get_wallet_transactions_sum."""
        tr_amount_1 = 1000
        tr_amount_2 = 700
        tr_amount_3 = 50

        # Сначала создадим транзакцию, чтобы на балансе хватало средств
        self.assertEqual(
            Transaction.get_wallet_transactions_sum(
                wallet_id=self.wallet_1.pk,
            ),
            0,
        )

        Transaction.objects.create(
            payee_id=self.wallet_1.pk,
            amount=tr_amount_1,
        )

        self.assertEqual(
            Transaction.get_wallet_transactions_sum(
                wallet_id=self.wallet_1.pk,
            ),
            tr_amount_1,
        )

        # ещё две, одну на пополнение, вторую на перевод из этого кошелька
        Transaction.objects.create(
            payee_id=self.wallet_1.pk,
            amount=tr_amount_2,
        )
        Transaction.objects.create(
            sender_id=self.wallet_1.pk,
            payee_id=self.wallet_2.pk,
            amount=tr_amount_3,
        )

        self.assertEqual(
            Transaction.get_wallet_transactions_sum(
                wallet_id=self.wallet_1.pk,
            ),
            tr_amount_1 + tr_amount_2 - tr_amount_3,
        )

    def test_good_transaction(self):
        """Проверка поведения, когда не хватает баланса."""
        client = APIClient()
        access_token = self._get_access_token(client=client)
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token,
        )

        # Сначала создадим транзакцию, чтобы на балансе хватало средств
        first_tr_amount = 1000
        self.assertEqual(
            Wallet.objects.get(
                pk=self.wallet_1.pk,
            ).balance,
            0,
        )

        Transaction.objects.create(
            payee_id=self.wallet_1.pk,
            amount=first_tr_amount,
        )
        Wallet.objects.filter(
            pk=self.wallet_1.pk,
        ).update(
            balance=Transaction.get_wallet_transactions_sum(
                wallet_id=self.wallet_1.pk,
            ),
        )

        self.assertEqual(
            Wallet.objects.get(
                pk=self.wallet_1.pk,
            ).balance,
            first_tr_amount,
        )

        # проверяем апи создание транзакции
        second_tr_amount = 200
        response = client.post(
            path='/wallet/transaction/',
            data={
                'sender': self.wallet_1.pk,
                'payee': self.wallet_2.pk,
                'amount': second_tr_amount,
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
            first_tr_amount - second_tr_amount,
        )

        self.assertEqual(
            Wallet.objects.get(
                pk=self.wallet_2.pk,
            ).balance,
            second_tr_amount,
        )

    def test_another_user(self):
        """
        Проверяем доступность кошелька другим пользователем.

        Авторизуемся за первого пользователя и пытаемся перевести со второго кошелька себе.
        """
        client = APIClient()
        access_token = self._get_access_token(client=client)
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token,
        )

        response = client.post(
            path='/wallet/transaction/',
            data={
                'sender': self.wallet_2.pk,
                'payee': self.wallet_1.pk,
                'amount': 1_000_000,
            },
        )
        self.assertEqual(response.json(), {'error': 'wallet not found'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_found_destination_wallet(self):
        """Проверяем доступность кошелька пополнения."""
        client = APIClient()
        access_token = self._get_access_token(client=client)
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token,
        )

        Transaction.objects.create(
            payee_id=self.wallet_1.pk,
            amount=1_000_000,
        )
        Wallet.objects.filter(
            pk=self.wallet_1.pk,
        ).update(
            balance=Transaction.get_wallet_transactions_sum(
                wallet_id=self.wallet_1.pk,
            ),
        )
        self.assertEqual(
            Wallet.objects.get(
                pk=self.wallet_1.pk,
            ).balance,
            1_000_000,
        )

        # отправляем на несуществующий кошелёк
        response = client.post(
            path='/wallet/transaction/',
            data={
                'sender': self.wallet_1.pk,
                'payee': self.wallet_2.pk + 1,
                'amount': 1_000,
            },
        )
        self.assertIn('payee', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем, что деньги не ушли
        self.assertEqual(
            Wallet.objects.get(
                pk=self.wallet_1.pk,
            ).balance,
            1_000_000,
        )
