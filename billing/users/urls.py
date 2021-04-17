from django.urls import path
from users.views import UserObtainTokenPairView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', UserObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
]
