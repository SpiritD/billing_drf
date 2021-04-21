from django.db import transaction
from django.db.models import F
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

        payee = serializer.validated_data['payee']
        amount = serializer.validated_data['amount']
        is_anonymous = serializer.validated_data.get('is_anonymous', False)
        comment = serializer.validated_data.get('comment', '')

        # при сохранении транзакции обновляем баланс кошелька
        with transaction.atomic():
            # создаём новую транзакцию
            Transaction.objects.create(
                sender=None,
                payee_id=payee.pk,
                amount=amount,
                is_anonymous=is_anonymous,
                comment=comment,
            )
            # обновляем баланс получателя транзакции
            Wallet.objects.filter(
                pk=payee.pk,
            ).update(
                balance=F('balance') + amount,
            )

        return Response(
            {},
            status=status.HTTP_200_OK,
        )
