from django.urls import path
from .views import TransactionList, DeleteView, transaction_delete

app_name = "transaction"

urlpatterns = [
    path("transctions/", TransactionList.as_view(), name="list"),
    path("delete/<str:pk>/", transaction_delete, name="delete"),
]
