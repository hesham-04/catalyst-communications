from django.urls import path

from .views import (
    IndexView, CashInHandUpdateView, AccountBalanceUpdateView,
    AccountBalanceList, AccountBalanceCreateView
)

app_name = 'assets'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('accounts/', AccountBalanceList.as_view(), name= 'accounts' ),
    path('accounts/create/', AccountBalanceCreateView.as_view(), name= 'accounts_create' ),


    path('cash-in-hand/update/', CashInHandUpdateView.as_view(), name='cash_in_hand_update'),
    path('account-balance/<str:pk>/', AccountBalanceUpdateView.as_view(), name='account_balance_update'),

]
