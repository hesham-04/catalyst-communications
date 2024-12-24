from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView

from src.core.mixins import AdminRequiredMixin
from src.services.transaction.models import Ledger
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.
class TransactionList(AdminRequiredMixin, LoginRequiredMixin, ListView):
    model = Ledger
    paginate_by = 30


def transaction_delete(request, pk):
    ledger = get_object_or_404(Ledger, pk=pk)

    if request.method == "POST":
        if "override_delete" in request.POST:

            # Handle override delete logic here
            ledger.delete(request, without_repercussions=True)
        else:
            ledger.delete(request, without_repercussions=False)
        return redirect("transaction:list")

    if request.method == "GET":
        context = {"object": ledger}
        return render(request, "transaction/ledger_confirm_delete.html", context)
