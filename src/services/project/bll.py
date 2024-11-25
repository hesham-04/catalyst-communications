from django.db import transaction
from src.services.assets.models import CashInHand, AccountBalance
from src.services.expense.models import Expense
from src.services.invoice.models import Invoice
from src.services.loan.models import Loan
from src.services.project.models import Project
from src.services.transaction.models import Ledger


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
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    # Handle destination addition
    project = Project.objects.select_for_update().get(pk=project_id)
    if destination == 'CASH':
        project.project_cash += amount
    elif destination == 'ACC':
        project.project_account_balance += amount

    project.save()

    # Handle source deduction
    if source == 'CASH':
        cash = CashInHand.objects.select_for_update().first()

        if not cash or cash.balance < amount:
            raise ValueError("Insufficient cash in hand.")
        cash.balance -= amount
        cash.save()

    elif source == 'ACC':
        account = AccountBalance.objects.select_for_update().first()

        if not account or account.balance < amount:
            raise ValueError("Insufficient account balance.")
        account.balance -= amount
        account.save()



    # Record the transaction in the ledger
    Ledger.objects.create(
        transaction_type="BUDGET_ASSIGN",
        project=project,
        amount=amount,
        source="Wallet: " + source,
        destination=destination,
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
def add_loan_to_project(project_id, amount, source, destination, reason):
    project = Project.objects.select_for_update().get(pk=project_id)
    project.total_budget_assigned += amount
    if destination == 'CASH':
        project.project_cash += amount
    elif destination == 'ACC':
        project.project_account_balance += amount
    project.save()

    Ledger.objects.create(
        transaction_type="CREATE_LOAN",
        project=project,
        amount=amount,
        source=source,
        destination=destination,
        reason=reason
    )

@transaction.atomic
def return_loan_to_lender(loan_id, project_id, amount, source, destination, reason):
    project = Project.objects.select_for_update().get(pk=project_id)
    loan = Loan.objects.select_for_update().get(pk=loan_id)

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if amount > loan.remaining_amount:
        raise ValueError("Amount cannot exceed the remaining loan balance.")

    loan.remaining_amount -= amount
    if loan.remaining_amount <= 0:
        loan.remaining_amount = 0
        loan.is_repaid = True
    loan.save()


    Expense.objects.create(
        project=project,
        description="Loan return",
        amount=amount,
        budget_source=source,
        category=None,
        vendor=None, #destination
        payment_status=Expense.PaymentStatus.UNPAID
    )

    Ledger.objects.create(
        transaction_type="RETURN_LOAN",
        project=project,
        amount=amount,
        source=source,
        destination=destination,
        reason=reason
    )

@transaction.atomic
def create_expense_calculations(project_id, amount, budget_source, reason=None):
    project = Project.objects.select_for_update().get(pk=project_id)

    if budget_source == 'CASH':
        project.project_cash -= amount

    elif budget_source == 'ACC':
        project.project_account_balance -= amount

    project.save()

    Ledger.objects.create(
        transaction_type="CREATE_EXPENSE",
        project=project,
        amount=amount,
        source=f"{budget_source} form {project.project_name}",
        destination=None,
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
def process_invoice_payment(invoice_id, destination,amount, account_id=None):
    try:
        invoice = Invoice.objects.select_for_update().get(pk=invoice_id)
        invoice.status = "PAID"
        invoice.save(update_fields=['status'])

        account = AccountBalance.objects.select_for_update().get(pk=account_id)

        ledger_reason = f"Payment for Invoice #{invoice.invoice_number} - Project:{invoice.project.project_name}"
        destination_name = None

        if destination == 'account' and account:
            account.balance += amount
            account.save(update_fields=['balance'])
            destination_name = f"Account: {account.account_name}"

        elif destination == 'project_cash':
            invoice.project.project_cash += amount
            invoice.project.save(update_fields=['project_cash'])
            destination_name = "Project Cash"

        elif destination == 'project_account_balance':
            invoice.project.project_account_balance += amount
            invoice.project.save(update_fields=['account_balance'])
            destination_name = "Project Account Balance"

        if destination_name:
            Ledger.objects.create(
                transaction_type="INVOICE_PAYMENT",
                project=invoice.project,
                amount=amount,
                source="Invoice",
                destination=destination_name,
                reason=ledger_reason
            )

        return True, "Invoice successfully paid and funds transferred."

    except Exception as e:
        # Handle unexpected errors
        return False, f"An error occurred while processing the payment: {str(e)}"
