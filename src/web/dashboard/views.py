from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from src.core.models import Transaction
from src.services.assets.models import CashInHand, AccountBalance
from src.services.customer.models import Customer

class HomeView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cash_in_hand = CashInHand.objects.first()
        account_balance = AccountBalance.objects.first()

        cash_in_hand_balance = cash_in_hand.balance if cash_in_hand else 0
        account_balance_balance = account_balance.balance if account_balance else 0

        # Add to context
        context['cash_in_hand'] = cash_in_hand_balance
        context['account_balance'] = account_balance_balance
        context['transactions'] = Transaction.objects.all()
        context['total_balance'] = cash_in_hand_balance + account_balance_balance
        context['customer_count'] = Customer.objects.count()  # More efficient than len(queryset)

        return context
