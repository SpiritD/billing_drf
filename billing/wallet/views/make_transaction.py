from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from wallet.models import Transaction
from wallet.serializers import CreateTransactionSerializer


class CreateTransactionView(ViewSetMixin, generics.CreateAPIView):
    """Создание транзакции между двумя кошельками."""

    serializer_class = CreateTransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):  # noqa: U100
        """Метод проверки и безопасного создания транзакции."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender_id = serializer.data['sender']
        payee_id = serializer.data['payee']
        amount = serializer.data['amount']
        is_anonymous = serializer.data['is_anonymous']
        comment = serializer.data['comment']

        # TODO: добавить проверку для транзакции

        # создаём новую транзакцию
        Transaction.objects.create(
            sender=sender_id,
            payee=payee_id,
            amount=amount,
            is_anonymous=is_anonymous,
            comment=comment,
        )
        return Response(
            {},
            status=status.HTTP_200_OK,
        )
