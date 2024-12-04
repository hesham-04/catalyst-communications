from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from src.services.transaction.models import Ledger


def get_monthly_income_expense(project_id):
    transactions = Ledger.objects.filter(project_id=project_id)

    monthly_income = (
        transactions.filter(transaction_type="INVOICE_PAYMENT")
        .annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    monthly_expense = (
        transactions.filter(transaction_type="CREATE_EXPENSE")
        .annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    income = [0] * 12
    expense = [0] * 12

    for item in monthly_income:
        month_index = item["month"] - 1
        income[month_index] = float(item["total"])

    for item in monthly_expense:
        month_index = item["month"] - 1
        expense[month_index] = float(item["total"])

    return income, expense
