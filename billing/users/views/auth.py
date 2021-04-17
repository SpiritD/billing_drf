from users.serializers import UserTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


class UserObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenObtainPairSerializer
