from django.urls import path
from .views import TransactionList

app_name = 'transaction'

urlpatterns = [
    path('transctions', TransactionList.as_view(), name='list')
]