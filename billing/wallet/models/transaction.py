from decimal import Decimal

from django.db import models
from django.db.models import Sum


class Transaction(models.Model):
    """Транзакции между пользователями."""

    # отправитель транзакции
    # при пополнении кошелька отправитель будет пустым
    sender = models.ForeignKey(
        'Wallet',
        on_delete=models.PROTECT,
        related_name='sent_payments',
        blank=True,
        null=True,
    )
    # получатель средств
    payee = models.ForeignKey(
        'Wallet',
        on_delete=models.PROTECT,
        related_name='received_payments',
    )

    # сумма транзакции с точностью до цента и менее 100_000_000
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # для возможности анонимной отправки средств
    is_anonymous = models.BooleanField(
        default=False,
    )
    comment = models.CharField(
        max_length=100,
        default='',
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = (
            '-created_at',
        )

    def __str__(self):
        """Отображение в админке."""
        return f'{self.sender} => {self.payee}: {self.amount}'

    @classmethod
    def get_wallet_transactions_sum(cls, wallet_id: int) -> Decimal:
        """
        Возвращает сумму всех транзакций на кошельке.

        :param wallet_id: id кошелька
        :return: сумма всех транзакций (актуальный баланс пользователя)
        """
        # из суммы транзакций, где кошелёк указан как получатель (payee) вычитаем
        # сумму транзакций, где этот же кошелёк указан как отправитель (sender)
        # TODO: Переписать на один запрос к бд
        input_sum = cls.objects.filter(
            payee_id=wallet_id,
        ).aggregate(input_sum=Sum('amount'))['input_sum'] or 0

        output_sum = cls.objects.filter(
            sender_id=wallet_id,
        ).aggregate(output_sum=Sum('amount'))['output_sum'] or 0

        return input_sum - output_sum
