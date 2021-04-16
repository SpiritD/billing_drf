from decimal import Decimal

from django.db import models

from users.models import User
from wallet.models import Transaction


class Wallet(models.Model):
    """Кошелёк пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )

    balance = models.DecimalField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'
        ordering = (
            '-created_at',
        )

    def __str__(self):
        """Отображение в админке."""
        return f'{self.user}: {self.balance}'

    def check_balance(self, update_balance: bool = False) -> Decimal:
        """
        Сверка баланса с суммой транзакций.

        По опыту считать баланс каждый раз как сумму транзакций очень накладно.
        При необходимости метод обновляет баланс кошелька.

        :param update_balance: если передано True, то обновляет поле balance значением, полученным
                               из суммы всех транзакций.
        :return: разница между балансом в кошельке и суммой транзакций. Если 0 - суммы совпадают.
        """
        transaction_balance = Transaction.get_user_transactions_sum(
            user_id=self.user_id,
        )
        diff_amount = self.balance - transaction_balance
        if diff_amount and update_balance:
            self.balance = transaction_balance
            self.save()
        return diff_amount
