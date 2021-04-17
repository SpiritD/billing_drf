from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Сериализатор для получения токена пользователя."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # добавляем кастомные поля
        token['email'] = user.email
        return token
