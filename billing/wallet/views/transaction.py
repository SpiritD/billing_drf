import redis_lock
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
from wallet.secure_transaction import (
    get_full_key,
    get_redis,
)
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

        sender = serializer.validated_data['sender']
        payee = serializer.validated_data['payee']
        amount = serializer.validated_data['amount']
        is_anonymous = serializer.validated_data.get('is_anonymous', False)
        comment = serializer.validated_data.get('comment', '')

        redis_client = get_redis()

        with redis_lock.Lock(redis_client, get_full_key(wallet_id=sender.pk)):
            # проверяем достаточно ли средств на кошельке и что кошелёк принадлежит пользователю
            try:
                sender_wallet: Wallet = Wallet.objects.get(
                    pk=sender.pk,
                    user=request.user,
                )
            except Wallet.DoesNotExist:
                return Response(
                    {'error': 'wallet not found'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if sender_wallet.balance < amount:
                # ошибка о нехвате средств
                return Response(
                    {'error': 'insufficient funds'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # при сохранении транзакции обновляем балансы кошельков
            # делаем это внутри лока, чтобы с кошелька отправителя не произошло второй транзакции
            # до обновления баланса
            with transaction.atomic():
                # создаём новую транзакцию
                Transaction.objects.create(
                    sender_id=sender.pk,
                    payee_id=payee.pk,
                    amount=amount,
                    is_anonymous=is_anonymous,
                    comment=comment,
                )
                # обновляем баланс отправителя транзакции
                Wallet.objects.filter(
                    pk=sender.pk,
                ).update(
                    balance=F('balance') - amount,
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
