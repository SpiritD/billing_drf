from django.db import transaction
from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from wallet.models import (
    Transaction,
    Wallet,
)
from wallet.serializers.deposit import CreateDepositSerializer


class CreateDepositView(ViewSetMixin, generics.CreateAPIView):
    """
    Создание транзакции на пополнение кошелька.

    Предусматривается только пополнение кошелька из внешних источников такие как
    платёжные системы (paypal, qiwi, walletone), банковские переводы и др.
    """

    serializer_class = CreateDepositSerializer
    queryset = Transaction.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):  # noqa: U100
        """Метод проверки и безопасного создания транзакции."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        payee_id = serializer.data['payee']
        amount = serializer.data['amount']
        is_anonymous = serializer.data.get('is_anonymous', False)
        comment = serializer.data.get('comment', '')

        # при сохранении транзакции обновляем баланс кошелька
        with transaction.atomic():
            # создаём новую транзакцию
            Transaction.objects.create(
                sender=None,
                payee_id=payee_id,
                amount=amount,
                is_anonymous=is_anonymous,
                comment=comment,
            )
            # обновляем баланс получателя транзакции
            Wallet.objects.filter(
                pk=payee_id,
            ).update(
                balance=Transaction.get_wallet_transactions_sum(
                    wallet_id=payee_id,
                ),
            )

        return Response(
            {},
            status=status.HTTP_200_OK,
        )
