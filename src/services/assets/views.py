from ctypes.wintypes import LGRPID

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Sum, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView

from .forms import CashInHandForm
from .models import CashInHand, AccountBalance
from ..project.bll import add_general_cash_in_hand
from ..transaction.models import Ledger
from ...core.mixins import AdminRequiredMixin
from ...web.dashboard.utils import ledger_filter


class IndexView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "assets/assets_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cash_in_hand = CashInHand.objects.first()
        context["cash_in_hand"] = cash_in_hand.balance if cash_in_hand else 0

        account_balance = AccountBalance.objects.aggregate(
            total_balance=Sum("balance")
        )["total_balance"]
        accounts = AccountBalance.objects.count()
        context["account_balance"] = account_balance if account_balance else 0
        context["accounts"] = accounts if accounts else 0

        return context


class CashInHandDetailView(AdminRequiredMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cashinhand = CashInHand.objects.first() or 0

        object_list = ledger_filter(source=cashinhand, destination=cashinhand)

        # Pagination setup
        page = request.GET.get("page", 1)
        paginator = Paginator(object_list, 20)

        try:
            paginated_object_list = paginator.page(page)
        except PageNotAnInteger:
            paginated_object_list = paginator.page(1)
        except EmptyPage:
            paginated_object_list = paginator.page(paginator.num_pages)

        context = {
            "cashinhand": cashinhand,
            "object_list": paginated_object_list,  # Use the paginated list here
        }
        return render(request, "assets/cashinhand.html", context)


# IDK IF IM SURE ABOUT ANY OF THIS.
class AddCashInHandView(AdminRequiredMixin, LoginRequiredMixin, FormView):
    form_class = CashInHandForm
    template_name = "assets/cashinhand_form.html"

    @transaction.atomic
    def form_valid(self, form):
        amount = form.cleaned_data["balance"]
        source_id = form.cleaned_data["source"]
        reason = form.cleaned_data["reason"]

        account = source_id
        if amount <= 0:
            form.add_error("balance", "The amount must be greater than zero.")
            return self.form_invalid(form)

        if amount > account.balance:
            form.add_error(
                "balance", "The amount you entered is greater than your balance."
            )
            return self.form_invalid(form)

        add_general_cash_in_hand(
            amount=amount,
            source=source_id,
            reason=reason,
        )
        # Show a success message and redirect to a success page
        messages.success(
            self.request,
            f"Cash in hand updated successfully. Added: {amount}",
        )
        messages.success(self.request, "Cash in hand updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Re-render the template with the form containing errors
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        # Redirect to a page of your choice after a successful form submission
        return reverse_lazy("assets:cash_list")


class CashInHandDeleteView(AdminRequiredMixin, LoginRequiredMixin, DeleteView):
    model = CashInHand
    template_name = "cashinhand_confirm_delete.html"
    success_url = reverse_lazy("cashinhand_list")


class AccountBalanceCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    model = AccountBalance
    fields = ["account_name", "balance"]
    success_url = reverse_lazy("assets:accounts")


class AccountBalanceList(AdminRequiredMixin, LoginRequiredMixin, ListView):
    model = AccountBalance
    paginate_by = 20


class AccountBalanceUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    model = AccountBalance
    fields = ["account_name", "balance"]
    success_url = reverse_lazy("assets:accounts")


class AccountBalanceDeleteView(AdminRequiredMixin, LoginRequiredMixin, DeleteView):
    model = AccountBalance
    template_name = "accountbalance_confirm_delete.html"
    success_url = reverse_lazy("assets:accounts")


class AccountBalanceDetailView(AdminRequiredMixin, LoginRequiredMixin, DetailView):
    model = AccountBalance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_list = ledger_filter(source=self.object, destination=self.object)

        paginator = Paginator(object_list, 20)
        page = self.request.GET.get("page")
        paginated_object_list = paginator.get_page(page)

        context["object_list"] = paginated_object_list

        return context
