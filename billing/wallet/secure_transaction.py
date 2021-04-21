import os
import string
from time import time as current_time

from django.utils.crypto import get_random_string
from redis import (
    Redis,
    StrictRedis,
)


def get_redis() -> Redis:
    """Получаем объект редиса с конфигурациями из окружения."""
    return StrictRedis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT', 6389),
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
