from django.urls import path

from wallet.views import CreateTransactionView


urlpatterns = [
    path('transaction/', CreateTransactionView.as_view({'post': 'create'})),
]
