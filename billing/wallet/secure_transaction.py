import os
import string
from time import time as current_time

from django.utils.crypto import get_random_string
from redis import (
    Redis,
    StrictRedis,
)

from wallet.constants import MAX_WALLET_LOCK_SECONDS


def get_redis() -> Redis:
    """Получаем объект редиса с конфигурациями из окружения."""
    return StrictRedis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        decode_responses=True,
    )


def generate_unique_value() -> str:
    """
    Генерация уникального значения.

    Берём уникальное значение, сгенерированное джанго + текущие микросекунды для большей надёжности.
    """
    current_mcs = str(current_time()).split('.')[-1]
    return get_random_string(
        length=10,
        allowed_chars=string.printable,
    ) + current_mcs


def get_full_key(wallet_id: int) -> str:
    """
    Генерируем ключ для редиса.

    Просто id кошелька не подойдёт, так как есть риск пересечения (да и просто непонятно будет).

    :param wallet_id: id кошелька
    :return: полный ключ для редиса
    """
    return f'tr_lock_{wallet_id}'


def set_lock_for_transaction(redis_client: Redis,
                             wallet_id: int,
                             unique_value: str) -> bool:
    """
    Устанавливаем ключ блокировки в редисе.

    1. Проверяем, что нет блокировки на транзакцию с кошелька пользователя.
    2. Устанавливаем свою блокировку.
    3. Проверяем, что именно наша блокировка установлена.
    Для каждого кошелька необходима отдельная блокировка

    :param redis_client: объект редиса
    :param wallet_id: id кошелька
    :param unique_value: уникальное значение, сгенерированное в этом запросе
    :return: успешно ли установлена блокировка для данного запроса
    """
    # ключ, обозначающий за блокировку для транзакции
    full_key = get_full_key(wallet_id=wallet_id)

    # если ключ уже установлен - вернём False
    if redis_client.get(name=full_key):
        return False

    # устанавливаем своё уникальное значение для блокировки
    redis_client.set(
        name=full_key,
        value=unique_value,
        ex=MAX_WALLET_LOCK_SECONDS,
    )

    # обязательно проверяем, что именно нами было установлено это значение
    if redis_client.get(full_key) != unique_value:
        return False

    return True


def remove_lock_for_transaction(redis_client: Redis,
                                wallet_id: int,
                                unique_value: str) -> None:
    """
    После завершения операций снимаем блокировку.

    :param redis_client: объект редиса
    :param wallet_id: id кошелька
    :param unique_value: уникальное значение, сгенерированное в этом запросе
    """
    # ключ, обозначающий за блокировку для транзакции
    full_key = get_full_key(wallet_id=wallet_id)

    if redis_client.get(full_key) == unique_value:
        redis_client.delete(full_key)
