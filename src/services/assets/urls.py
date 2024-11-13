from django.urls import path

from .views import (
    IndexView, CashInHandUpdateView, AccountBalanceUpdateView
)

app_name = 'assets'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('cash-in-hand/update/', CashInHandUpdateView.as_view(), name='cash_in_hand_update'),
    path('account-balance/update/', AccountBalanceUpdateView.as_view(), name='account_balance_update'),

]
