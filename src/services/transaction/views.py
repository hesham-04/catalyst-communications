from django.shortcuts import render
from django.views.generic import ListView

from src.services.transaction.models import Ledger


# Create your views here.
class TransactionList(ListView):
    model = Ledger