from django.db.models import Sum
from django.views.generic import TemplateView

from src.services.assets.models import CashInHand, AccountBalance
from src.services.customer.models import Customer
from src.services.invoice.models import Invoice
from src.services.loan.models import Loan
from src.services.transaction.models import Ledger
from src.services.vendor.models import Vendor
from src.web.dashboard.utils import get_monthly_income_expense


class HomeView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        income, expense = get_monthly_income_expense()

        cash_in_hand = CashInHand.objects.first()
        cash_in_hand_balance = cash_in_hand.balance if cash_in_hand else 0
        account_balance_balance = AccountBalance.objects.aggregate(total=Sum('balance'))['total'] or 0

        context['cash_in_hand'] = cash_in_hand_balance
        context['income'] = income
        context['expense'] = expense
        context['account_balance'] = account_balance_balance
        context['total_balance'] = cash_in_hand_balance + account_balance_balance
        context['customer_count'] = Customer.objects.count()
        context['payable'] = Loan.calculate_total_unpaid_amount()
        context['receivables'] = Invoice.calculate_total_receivables()
        context['top_vendors'] = Vendor.objects.order_by('-total_expense')[:8]
        context['transactions'] = Ledger.objects.order_by('-created_at')[:8]
        return context
