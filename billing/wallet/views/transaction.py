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
from wallet.secure_transaction import (
    generate_unique_value,
    get_redis,
    remove_lock_for_transaction,
    set_lock_for_transaction,
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

        sender_id = serializer.data['sender']
        payee_id = serializer.data['payee']
        amount = serializer.data['amount']
        is_anonymous = serializer.data['is_anonymous']
        comment = serializer.data['comment']

        redis_client = get_redis()
        unique_value = generate_unique_value()

        # чтобы не плодить if сразу вернём ошибку, если не смогли поставить блокировку
        if not set_lock_for_transaction(
            redis_client=redis_client,
            wallet_id=sender_id,
            unique_value=unique_value,
        ):
            return Response(
                {},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # проверяем достаточно ли средств на кошельке
        sender_wallet: Wallet = Wallet.objects.get(
            user_id=sender_id,
        )
        if sender_wallet.balance < amount:
            remove_lock_for_transaction(
                redis_client=redis_client,
                wallet_id=sender_id,
                unique_value=unique_value,
            )
            # ошибка о нехвате средств
            return Response(
                {'error': 'insufficient funds'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # при сохранении транзакции обновляем балансы кошельков
        with transaction.atomic():
            # создаём новую транзакцию
            Transaction.objects.create(
                sender=sender_id,
                payee=payee_id,
                amount=amount,
                is_anonymous=is_anonymous,
                comment=comment,
            )
            # обновляем баланс отправителя транзакции
            Wallet.objects.filter(
                user_id=sender_id,
            ).update(
                balance=Transaction.get_wallet_transactions_sum(
                    wallet_id=sender_id,
                ),
            )
            # обновляем баланс получателя транзакции
            Wallet.objects.filter(
                user_id=payee_id,
            ).update(
                balance=Transaction.get_wallet_transactions_sum(
                    wallet_id=payee_id,
                ),
            )

        # снимаем блокировку с кошелька
        remove_lock_for_transaction(
            redis_client=redis_client,
            wallet_id=sender_id,
            unique_value=unique_value,
        )

        return Response(
            {},
            status=status.HTTP_200_OK,
        )
