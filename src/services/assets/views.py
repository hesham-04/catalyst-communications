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
from ..transaction.models import Ledger


class IndexView(TemplateView):
    template_name = 'assets/assets_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cash_in_hand = CashInHand.objects.first()
        context['cash_in_hand'] = cash_in_hand.balance if cash_in_hand else 0

        account_balance = AccountBalance.objects.aggregate(total_balance=Sum('balance'))['total_balance']
        accounts = AccountBalance.objects.count()
        context['account_balance'] = account_balance if account_balance else 0
        context['accounts'] = accounts if accounts else 0

        return context


class CashInHandDetailView(View):
    def get(self, request, *args, **kwargs):
        cashinhand = CashInHand.objects.first() or 0

        object_list = Ledger.objects.filter(
            Q(source__icontains="Wallet: Cash In Hand") | Q(destination__icontains="Wallet: Cash In Hand")
        )

        # Pagination setup
        page = request.GET.get('page', 1)
        paginator = Paginator(object_list, 20)

        try:
            paginated_object_list = paginator.page(page)
        except PageNotAnInteger:
            paginated_object_list = paginator.page(1)
        except EmptyPage:
            paginated_object_list = paginator.page(paginator.num_pages)

        context = {
            'cashinhand': cashinhand,
            'object_list': paginated_object_list,  # Use the paginated list here
        }
        return render(request, 'assets/cashinhand.html', context)


class AddCashInHandView(FormView):
    form_class = CashInHandForm
    template_name = 'assets/cashinhand_form.html'

    def form_valid(self, form):
        amount = form.cleaned_data['balance']
        source_id = form.cleaned_data['source']
        reason = form.cleaned_data['reason']

        try:
            account = source_id
        except AccountBalance.DoesNotExist:
            form.add_error('source', "The selected source does not exist.")
            return self.form_invalid(form)

        if amount > account.balance:
            form.add_error('balance', "The amount you entered is greater than your balance.")
            return self.form_invalid(form)

        with transaction.atomic():
            account.balance -= amount
            account.save(update_fields=['balance'])

            # Add to CashInHand
            cashinhand, created = CashInHand.objects.get_or_create(defaults={'balance': 0})
            cashinhand.balance += amount
            cashinhand.save(update_fields=['balance'])

            # Create ledger entry
            Ledger.objects.create(
                transaction_type="ADD_CASH",
                amount=amount,
                source=f"Wallet: {account.account_name} ({account.pk})",
                destination=f"Wallet: Cash In Hand ({cashinhand.pk})",
                reason=reason
            )

        # Show a success message and redirect to a success page
        messages.success(self.request, "Cash in hand updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Re-render the template with the form containing errors
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        # Redirect to a page of your choice after a successful form submission
        return reverse_lazy('assets:cash_list')


class CashInHandDeleteView(DeleteView):
    model = CashInHand
    template_name = 'cashinhand_confirm_delete.html'
    success_url = reverse_lazy('cashinhand_list')


""" Account Balance"""


class AccountBalanceCreateView(LoginRequiredMixin, CreateView):
    model = AccountBalance
    fields = ['account_name', 'balance']
    success_url = reverse_lazy('assets:accounts')


class AccountBalanceList(LoginRequiredMixin, ListView):
    model = AccountBalance
    paginate_by = 20


class AccountBalanceUpdateView(LoginRequiredMixin, UpdateView):
    model = AccountBalance
    fields = ['account_name', 'balance']
    success_url = reverse_lazy('assets:accounts')


class AccountBalanceDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountBalance
    template_name = 'accountbalance_confirm_delete.html'
    success_url = reverse_lazy('assets:accounts')


class AccountBalanceDetailView(LoginRequiredMixin, DetailView):
    model = AccountBalance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_list = Ledger.objects.filter(
            Q(source__icontains=f"Wallet: {self.object.account_name}") | Q(
                destination__icontains=f"Wallet: {self.object.account_name}")
        )

        paginator = Paginator(object_list, 20)
        page = self.request.GET.get('page')
        paginated_object_list = paginator.get_page(page)

        context['object_list'] = paginated_object_list

        return context
