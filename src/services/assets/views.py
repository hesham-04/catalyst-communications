from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from src.services.assets.forms import CashInHandForm, AccountBalanceForm
from src.services.assets.models import CashInHand, AccountBalance


class IndexView(TemplateView):
    template_name = 'assets/assets_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cash_in_hand = CashInHand.objects.first()
        context['cash_in_hand'] = cash_in_hand.balance if cash_in_hand else 0

        account_balance = AccountBalance.objects.first()
        context['account_balance'] = account_balance.balance if account_balance else 0
        return context




class CashInHandUpdateView(UpdateView):
    model = CashInHand
    template_name = 'assets/cash_in_hand_update.html'
    form_class = CashInHandForm
    success_url = reverse_lazy('assets:index')

    def get_object(self):
        return CashInHand.objects.first() or CashInHand.objects.create(balance=0)


class AccountBalanceUpdateView(UpdateView):
    model = AccountBalance
    template_name = 'assets/account_balance_update.html'
    form_class = AccountBalanceForm
    success_url = reverse_lazy('assets:index')

    def get_object(self):
        return AccountBalance.objects.first() or AccountBalance.objects.create(account_name='Default Account', balance=0.00)