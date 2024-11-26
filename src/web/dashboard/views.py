from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from src.services.assets.models import CashInHand, AccountBalance
from src.services.customer.models import Customer
from src.services.expense.models import Expense


class HomeView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cash_in_hand = CashInHand.objects.first()


        cash_in_hand_balance = cash_in_hand.balance if cash_in_hand else 0
        account_balance_balance = AccountBalance.objects.aggregate(total=Sum('balance'))['total'] or 0

        context['cash_in_hand'] = cash_in_hand_balance
        context['account_balance'] = account_balance_balance
        context['total_balance'] = cash_in_hand_balance + account_balance_balance
        context['customer_count'] = Customer.objects.count()
        context['payable'] = Expense.calculate_total_expenses(project_id=None)

        return context
