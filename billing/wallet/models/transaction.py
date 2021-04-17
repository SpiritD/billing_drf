from decimal import Decimal

from django.db import models
from django.db.models import Sum

from users.models import User


class Transaction(models.Model):
    """Транзакции между пользователями."""

    # отправитель транзакции
    sender = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sent_payments',
    )
    # получатель средств
    payee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='received_payments',
    )

    # сумма транзакции с точностью до цента и менее 100_000_000
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # для возможности анонимной отправки средств
    is_anonymous = models.BooleanField(default=False)
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
    def get_user_transactions_sum(cls, user_id: int) -> Decimal:
        """
        Возвращает сумму всех транзакций пользователя.

        :param user_id: id пользователя
        :return: сумма всех транзакций (актуальный баланс пользователя)
        """
        return cls.objects.filter(
            user_id=user_id,
        ).aggregate(
            total=Sum('amount'),
        )['total']
