from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    RegisterView,
    UserObtainTokenPairView,
)


urlpatterns = [
    path('login/', UserObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
]
