from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from wallet.constants import MIN_DEPOSIT_AMOUNT
from wallet.models import Transaction


class CreateDepositSerializer(ModelSerializer):
    """Сериализатор для пополнения средств."""

    amount = serializers.IntegerField(min_value=MIN_DEPOSIT_AMOUNT)

    class Meta:
        model = Transaction
        fields = (
            'payee',
            'amount',
            'is_anonymous',
            'comment',
        )
        extra_kwargs = {
            'payee': {'required': True},
            'amount': {'required': True},
        }
