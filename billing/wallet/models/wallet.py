from django.db import models

from users.models import User


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
