from django.urls import path

from .views import (
    IndexView, AccountBalanceUpdateView,
    AccountBalanceList, AccountBalanceCreateView, CashInHandDetailView, AddCashInHandView, AccountBalanceDetailView
)

app_name = 'assets'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('accounts/', AccountBalanceList.as_view(), name= 'accounts' ),
    path('accounts/create/', AccountBalanceCreateView.as_view(), name= 'accounts_create'),
    path('account/<str:pk>/update/', AccountBalanceUpdateView.as_view(), name='account_balance_update'),
    path('account/<str:pk>/detail/', AccountBalanceDetailView.as_view(), name='account-detail'),


    path('cash-in-hand/add/', AddCashInHandView.as_view(), name='add-cash-in-hand' ),
    path('cash-in-hand/', CashInHandDetailView.as_view(), name='cash_list'),

]
