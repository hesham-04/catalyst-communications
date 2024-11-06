from django.views.generic import TemplateView
from src.core.models import Transaction, CashInHand, AccountBalance
from src.services.customer.models import Customer


class HomeView(TemplateView):
    template_name = 'dashboard/dashboard.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cash_in_hand = CashInHand.objects.first()
        account_balance = AccountBalance.objects.first()
        context['cash_in_hand'] = cash_in_hand.balance
        context['account_balance'] = account_balance.balance
        context['transactions'] = Transaction.objects.all()
        context['total_balance'] = cash_in_hand.balance + account_balance.balance
        context['customer_count'] = len(Customer.objects.all())
        return context