from logging import getLogger
# Django import
from typing import Optional

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models


logger = getLogger(__name__)


class UserQuerySet(models.query.QuerySet):
    """Переопределение QuerySet для модели User."""

    def delete(self):
        """Вместо удаления вызываем метод для мягкой очистки базы."""
        for user in self:
            user.delete()


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):  # type: ignore  # noqa: Z454
    """Переопределение менеджера для модели User."""

    def get_by_natural_key(self, username):
        """Для получения пользователя по полю KEY_FIELD модели."""
        # Запрос не должен учитывать регистр
        case_insensitive_username_field = f'{self.model.KEY_FIELD}__iexact'
        user = self.filter(
            **{case_insensitive_username_field: username},
        ).first()
        if not user:
            raise User.DoesNotExist
        return user

    def create_user(self, email, password=None, **kwargs):
        """Создание пользователя."""
        if not email:
            raise ValueError('Users must have an email address')

        # email сохраняем в lower case
        user = self.model(
            email=self.normalize_email(email.lower()),
            **kwargs,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        """Создание пользователя с правами администратора."""
        user = self.create_user(
            email,
            password=password,
            **kwargs,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def delete(self):
        """Override method."""
        logger.warning("You can't remove all users using UserManager")

    def get_query_set(self):
        """Возвращаем наш queryset."""
        return UserQuerySet(self.model, using=self._db)


class User(AbstractBaseUser, PermissionsMixin):  # type: ignore
    """User model."""

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,  # noqa: Z432
        unique=True,
    )

    first_name = models.CharField(max_length=30, null=True)  # noqa: Z432
    last_name = models.CharField(max_length=30, null=True, blank=True)  # noqa: Z432

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # для подтверждения учётки
    verified = models.BooleanField(default=False)

    # деактивирование учётки
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    objects = UserManager()  # noqa: Z110
    KEY_FIELD = 'email'  # noqa: Z115

    class Meta:
        db_table = 'users'
        ordering = ('-created_at',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        """Repr in admin and console."""
        return self.email

    def get_full_name(self) -> str:
        """Возвращаем имя пользователя, если заполнено, иначе email."""
        full_name = f'{self.first_name or ""} {self.last_name or ""}'.strip()
        return full_name if full_name else self.email

    def email_user(self,
                   subject: str,
                   message: str,
                   from_email: Optional[str] = None,
                   **kwargs):
        """
        Отправка письма пользователю.

        Данный метод не предназначен для использования в проде.
        Для прода нужно заменять send_mail.

        :param subject: тема письма
        :param message: текст письма
        :param from_email: почтовый адрес отправителя
        :param kwargs: дополнительные параметры, например для подстановки в шаблон письма,
                       идентификатор самого шаблона и т.д.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
