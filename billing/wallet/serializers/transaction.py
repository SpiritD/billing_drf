from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from wallet.constants import MIN_TRANSACTION_AMOUNT
from wallet.models import Transaction


class CreateTransactionSerializer(ModelSerializer):
    """Сериализатор для транзакции между двумя кошельками."""

    amount = serializers.IntegerField(min_value=MIN_TRANSACTION_AMOUNT)

    class Meta:
        model = Transaction
        fields = (
            'sender',
            'payee',
            'amount',
            'is_anonymous',
            'comment',
        )
        extra_kwargs = {
            'sender': {'required': True},
            'payee': {'required': True},
            'amount': {'required': True},
        }
