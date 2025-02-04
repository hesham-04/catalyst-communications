from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView

from .forms import CashInHandForm, TransferForm
from .models import CashInHand, AccountBalance
from ..project.bll import add_general_cash_in_hand, add_account_balance, transfer_balance
from ...core.mixins import AdminRequiredMixin
from ...web.dashboard.utils import ledger_filter
from .forms import AddBalance

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
    template_name = "assets/accountbalance_confirm_delete.html"
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

class AddAccountBalanceView(AdminRequiredMixin, LoginRequiredMixin, FormView):
    form_class = AddBalance
    template_name = "assets/add_balance.html"

    def get_object(self):
        pk = self.kwargs.get("pk")
        return AccountBalance.objects.get(pk=pk)

    @transaction.atomic
    def form_valid(self, form):
        amount = form.cleaned_data["balance"]
        source = form.cleaned_data["source"]
        account = self.get_object()

        if amount <= 0:
            form.add_error("balance", "The amount must be greater than zero.")
            return self.form_invalid(form)

        add_account_balance(
            amount=amount,
            account_pk=account.pk,
            reason=source,
        )
        # Show a success message and redirect to a success page
        messages.success(
            self.request,
            f"Account balance updated successfully. Added: {amount}",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        # Re-render the template with the form containing errors
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        # Redirect to a page of your choice after a successful form submission
        return reverse_lazy("assets:accounts")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = self.get_object()
        return context



class AccountBalanceTransferView(LoginRequiredMixin, AdminRequiredMixin, FormView):
    template_name = "assets/transfer_balance.html"
    form_class = TransferForm

    def get_account(self):
        """Retrieve the account or return 404 if not found."""
        return get_object_or_404(AccountBalance, pk=self.kwargs.get("pk"))

    def get_form_kwargs(self):
        """Pass the current account to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["current_account"] = self.get_account()
        return kwargs

    def form_valid(self, form):
        """Handle successful form submission."""
        account = self.get_account()
        destination = form.cleaned_data["destination"]
        amount = form.cleaned_data["amount"]
        reason = form.cleaned_data["reason"]

        if amount <= 0:
            form.add_error("amount", "The amount must be greater than zero.")
            return self.form_invalid(form)

        if amount > account.balance:
            form.add_error("amount", "The amount you entered is greater than your balance.")
            return self.form_invalid(form)

        # Perform the transfer
        transfer_balance(amount=amount, source=account, destination=destination, reason=reason)

        messages.success(self.request, f"Transferred {amount} to {destination.account_name} successfully.")
        return redirect(reverse("assets:account-detail", kwargs={"pk": account.pk}))

    def form_invalid(self, form):
        """Handle invalid form submissions."""
        return self.render_to_response(self.get_context_data(form=form, account=self.get_account()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = self.get_account()
        return context