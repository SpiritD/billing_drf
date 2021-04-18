from django.urls import path

from wallet.views import (
    CreateDepositView,
    CreateTransactionView,
)


urlpatterns = [
    path('deposit/', CreateDepositView.as_view({'post': 'create'})),
    path('transaction/', CreateTransactionView.as_view({'post': 'create'})),
]
