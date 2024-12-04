from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from src.services.transaction.models import Ledger


# Create your views here.
class TransactionList(LoginRequiredMixin, ListView):
    model = Ledger
    paginate_by = 30
