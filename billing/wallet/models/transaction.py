from django.db import models

from users.models import User


class Transaction(models.Model):
    """Транзакции между пользователями."""

    # отправитель транзакции
    sender = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    # получатель средств
    payee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )

    # сумма транзакции
    amount = models.DecimalField()

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
