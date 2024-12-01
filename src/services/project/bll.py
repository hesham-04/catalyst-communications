from django.db import transaction

from src.services.assets.models import CashInHand, AccountBalance
from src.services.expense.models import Expense
from src.services.invoice.models import Invoice
from src.services.loan.models import Loan, Lender
from src.services.project.models import Project
from src.services.transaction.models import Ledger
from src.services.vendor.models import Vendor


@transaction.atomic
def add_budget_to_project(project_id, amount, source, destination, reason):
    """
    Adjusts the budget of a project based on the source and destination of funds.
    :param reason:
    :param project_id: The ID of the project
    :param amount: The amount to transfer
    :param source: The source of the funds ('CASH', 'ACC')
    :param destination: The destination for the funds ('CASH', 'ACC')

    """

    # Handle destination addition
    project = Project.objects.select_for_update().get(pk=project_id)
    project.project_account_balance += amount
    project.save()

    # Handle source deduction
    account = AccountBalance.objects.get(pk=source.pk)

    if not account or account.balance < amount:
        raise ValueError("Insufficient account balance.")
    account.balance -= amount
    account.save()

    # Record the transaction in the ledger
    Ledger.objects.create(
        transaction_type="BUDGET_ASSIGN",
        project=project,
        amount=amount,
        source=f"Wallet: {source.account_name} ({source.pk})",
        destination=f"Project: {project.project_name} ACC ({project.pk})",
        reason=reason
    )

    return {
        "message": "Budget successfully assigned to the project.",
        "project_id": project_id,
        "amount": amount,
        "source": source,
        "destination": destination,
    }


@transaction.atomic
def add_loan_to_project(project_id, amount, source, reason, destination=None):
    project = Project.objects.select_for_update().get(pk=project_id)
    project.total_budget_assigned += amount

    project.project_account_balance += amount
    project.save()

    lender = Lender.objects.get(pk=source.pk)

    Ledger.objects.create(
        transaction_type="CREATE_LOAN",
        project=project,
        amount=amount,
        source=f"Loan: {lender.name} ({lender.pk})",
        destination=f"Project: {project.project_name} ACC ({project.pk})",
        reason=reason
    )


@transaction.atomic
def return_loan_to_lender(loan_id, project_id, amount, source, destination, reason):
    project = Project.objects.select_for_update().get(pk=project_id)
    loan = Loan.objects.select_for_update().get(pk=loan_id)

    loan.remaining_amount -= amount
    if loan.remaining_amount <= 0:
        loan.remaining_amount = 0
        loan.is_repaid = True
    loan.save()

    project.project_account_balance -= amount

    project.save()

    Expense.objects.create(
        project=project,
        description="Loan return",
        amount=amount,
        budget_source='Project ACC',
        category=None,
        vendor=None,  # destination
        payment_status=Expense.PaymentStatus.PAID
    )

    Ledger.objects.create(
        transaction_type="RETURN_LOAN",
        project=project,
        amount=amount,
        source=f"Project: {project.project_name} ACC ({project.pk})",
        destination=f"Lender: {loan.lender.name} ({loan.id})",
        reason=reason
    )


@transaction.atomic
def create_expense_calculations(project_id, amount, budget_source, destination, reason=None):
    project = Project.objects.select_for_update().get(pk=project_id)

    if budget_source == 'CASH':
        project.project_cash -= amount

    elif budget_source == 'ACC':
        project.project_account_balance -= amount

    project.save()
    vendor = Vendor.objects.get(pk=destination)
    vendor.total_expense += amount
    vendor.save()

    Ledger.objects.create(
        transaction_type="CREATE_EXPENSE",
        project=project,
        amount=amount,
        source=f"Project {project.project_name} {budget_source} ({project.pk})",
        destination=f"Vendor: {vendor.name} ({vendor.pk})",
        reason=reason,
    )


@transaction.atomic
def pay_expense(project_id, amount, budget_source, reason=None, expense_id=None):
    project = Project.objects.select_for_update().get(pk=project_id)
    expense = Expense.objects.select_for_update().get(pk=expense_id)
    expense.payment_status = Expense.PaymentStatus.PAID
    if budget_source == 'CASH':
        project.project_cash -= amount

    elif budget_source == 'ACC':
        project.project_account_balance -= amount

    project.save()

    Ledger.objects.create(
        transaction_type="PAY_EXPENSE",
        project=project,
        amount=amount,
        source=f"{budget_source} form {project.project_name}",
        destination=None,
        reason=reason,
    )


@transaction.atomic
def process_invoice_payment(invoice_id, destination, amount, account_id=None):
    try:
        invoice = Invoice.objects.select_for_update().get(pk=invoice_id)
        invoice.status = "PAID"
        invoice.save(update_fields=['status'])

        if account_id: account = AccountBalance.objects.select_for_update().get(pk=account_id)

        ledger_reason = f"Payment for Invoice"

        if destination == 'account' and account:
            account.balance += amount
            account.save(update_fields=['balance'])

        Ledger.objects.create(
            transaction_type="INVOICE_PAYMENT",
            project=invoice.project,
            amount=amount,
            source=f"Invoice Paid: {invoice.client_name} ({invoice.pk})",
            destination=f"Wallet: {account.account_name} ({account.pk})",
            reason=ledger_reason
        )

        return True, "Invoice successfully paid and funds transferred."

    except Exception as e:
        # Handle unexpected errors
        return False, f"An error occurred while processing the payment: {str(e)}"


@transaction.atomic
def create_journal_expense_calculations(category, reason, destination, amount, source, account_pk=None):
    try:
        if source == "ACC":
            account = AccountBalance.objects.select_for_update().get(pk=account_pk)
            account.balance -= amount
            account.save(update_fields=['balance'])
        else:
            cashinhand = CashInHand.objects.first()
            cashinhand.balance -= amount
            cashinhand.save(update_fields=['balance'])

        vendor = Vendor.objects.get(pk=destination) if destination else None
        if vendor:
            vendor.total_expense += amount
            vendor.save(update_fields=['total_expense'])

        # Create a ledger entry after updating the account/cash balance
        Ledger.objects.create(
            transaction_type="CREATE_JOURNAL_EXPENSE",
            amount=amount,
            source=f"Wallet: {account.account_name} ({account.pk})" if source == "ACC" else f"Wallet: Cash In Hand ({cashinhand.pk})",
            destination=f"Vendor: {vendor.name} ({vendor.pk})" if vendor else f"Category: {category.name}",
            reason=reason + " " + category.name
        )
        return True, "Journal Entry Successfully created"


    except Exception as e:
        # Catch any unexpected exceptions
        return False, f"An error occurred while processing the payment: {str(e)}"

    return True, "Transaction successful"

