from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import UserTokenObtainPairSerializer


class UserObtainTokenPairView(TokenObtainPairView):
    """Авторизация пользователя."""

    permission_classes = (AllowAny,)
    serializer_class = UserTokenObtainPairSerializer
