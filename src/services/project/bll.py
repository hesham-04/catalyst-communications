from os import access
from threading import active_count

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from src.services.assets.models import CashInHand, AccountBalance
from src.services.expense.models import Expense
from src.services.invoice.models import Invoice
from src.services.loan.models import Loan, Lender, MiscLoan
from src.services.project.models import Project
from src.services.quotation.models import QuotationGeneral
from src.services.transaction.models import Ledger
from src.services.vendor.models import Vendor


# VALIDATION ✔
@transaction.atomic
def add_budget_to_project(project_id, amount, source, reason):
    """
    The Budget To A Project Can only be assigned form a Bank account Instance
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
    account.balance -= amount
    account.save()

    # Record the transaction in the ledger
    Ledger.objects.create(
        transaction_type="BUDGET_ASSIGN",
        project=project,
        amount=amount,
        source_content_type=ContentType.objects.get_for_model(account),
        source_object_id=account.pk,
        destination_content_type=ContentType.objects.get_for_model(project),
        destination_object_id=project.pk,
        reason=reason,
    )


# VALIDATION ✔
@transaction.atomic
def add_loan_to_project(project_id, amount, source, reason):
    project = Project.objects.select_for_update().get(pk=project_id)
    project.project_account_balance += amount
    project.save(update_fields=["project_account_balance"])

    loan = Lender.objects.get(pk=source.pk)

    Ledger.objects.create(
        transaction_type="CREATE_LOAN",
        project=project,
        amount=amount,
        source_content_type=ContentType.objects.get_for_model(loan),
        source_object_id=loan.pk,
        destination_content_type=ContentType.objects.get_for_model(project),
        destination_object_id=project.pk,
        reason=reason,
    )


# VALIDATION ✔
@transaction.atomic
def return_loan_to_lender(project_id, loan_id, amount, reason):
    project = Project.objects.select_for_update().get(pk=project_id)
    loan = Loan.objects.select_for_update().get(pk=loan_id)

    # Subtract from the loan remaining amount
    loan.update_remaining_amount(amount)
    project.project_account_balance -= amount

    loan.save()
    project.save()

    # Create an Expense instance for the loan return.
    # Is the Expense model even use anywhere for fin calcs.
    expense = Expense.objects.create(
        project=project,
        description="Loan Return",
        amount=amount,
        budget_source="Project Account Balance",
        vendor=None,  # Destination but NONE
        payment_status=Expense.PaymentStatus.PAID,
    )

    # Record the transaction in the ledger
    Ledger.objects.create(
        transaction_type="RETURN_LOAN",
        project=project,
        amount=amount,
        source_content_type=ContentType.objects.get_for_model(project),
        source_object_id=project.pk,
        destination_content_type=ContentType.objects.get_for_model(loan),
        destination_object_id=loan.pk,
        expense=expense,
        reason=reason,
    )


# VALIDATION ✔
@transaction.atomic
def create_expense_calculations(
    project_id, amount, budget_source, vendor_pk, category, reason, expense
):
    project = Project.objects.select_for_update().get(pk=project_id)

    # Handle source deduction
    if budget_source == "CASH":
        project.project_cash -= amount

    elif budget_source == "ACC":
        project.project_account_balance -= amount

    # NO DESTINATION FOR EXPENSE
    # Vendor Usage is determined from the self.total_expense method defined in the vendor model

    project.save()
    vendor = Vendor.objects.get(pk=vendor_pk)

    Ledger.objects.create(
        transaction_type="CREATE_EXPENSE",
        project=project,
        amount=amount,
        source_content_type=ContentType.objects.get_for_model(project),
        source_object_id=project.pk,
        destination_content_type=ContentType.objects.get_for_model(vendor),
        destination_object_id=vendor.pk,
        expense_category=category,  # FIXED LATER. CHECKED AGAIN ✔
        reason=reason,
        expense=expense,
    )


# VALIDATION - TEMPORARILY DEPRECATED †
@transaction.atomic
def pay_expense(project_id, amount, budget_source, reason=None, expense_id=None):
    project = Project.objects.select_for_update().get(pk=project_id)
    expense = Expense.objects.select_for_update().get(pk=expense_id)
    expense.payment_status = Expense.PaymentStatus.PAID
    if budget_source == "CASH":
        project.project_cash -= amount

    elif budget_source == "ACC":
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


# VALIDATION ✔
@transaction.atomic
def process_invoice_payment(invoice_id, amount, account_id, q=False):
    try:
        if q:
            invoice = QuotationGeneral.objects.select_for_update().get(pk=invoice_id)
            invoice.status = "PAID"
            invoice.save(update_fields=["status"])
        else:
            invoice = Invoice.objects.select_for_update().get(pk=invoice_id)
            invoice.status = "PAID"
            invoice.save(update_fields=["status"])

        account = AccountBalance.objects.select_for_update().get(pk=account_id)
        account.balance += amount
        account.save(update_fields=["balance"])

        Ledger.objects.create(
            transaction_type="INVOICE_PAYMENT",
            project=invoice.project if not q else None,
            amount=amount,
            source_content_type=ContentType.objects.get_for_model(invoice),
            source_object_id=invoice.pk,
            destination_content_type=ContentType.objects.get_for_model(account),
            destination_object_id=account.pk,
            reason="Invoice Payment",
        )

        return True, "Invoice successfully paid and funds transferred."

    except Exception as e:
        # Handle unexpected errors
        return False, f"An error occurred while processing the payment: {str(e)}"


# VALIDATION ✔
@transaction.atomic
def create_journal_expense_calculations(
    category, reason, vendor, amount, misc_expense, source, account_pk=None
):
    """
    Creates a ledger entry for a journal expense.

    :param category: The category of the expense
    :param reason: The reason for the expense
    :param vendor: The vendor id to which the expense is made
    :param misc_expense: The misc expense instance for the ledger
    :param amount: The amount of the expense
    :param source: The source of the expense (CASH or ACC)
    :param account_pk: The account id from which the expense is made (if source is ACC)
    :return: A tuple containing a boolean indicating success and a message
    """
    try:
        # Update the account/cash balance
        source_account = None
        if source == "ACC":
            account = AccountBalance.objects.select_for_update().get(pk=account_pk)
            account.balance -= amount
            account.save(update_fields=["balance"])
            source_account = account
        else:
            cash_in_hand = CashInHand.objects.first()
            cash_in_hand.balance -= amount
            cash_in_hand.save(update_fields=["balance"])
            source_account = cash_in_hand

        # Create a ledger entry after updating the account/cash balance
        Ledger.objects.create(
            transaction_type="MISC_EXPENSE",
            amount=amount,
            source_content_type=ContentType.objects.get_for_model(source_account),
            source_object_id=source_account.pk,
            destination_content_type=ContentType.objects.get_for_model(vendor),
            destination_object_id=vendor.pk,
            reason=reason,
            misc_expense=misc_expense,
            expense_category=category,
        )
        return True, "Journal Entry Successfully created"

    except Exception as e:
        return False, f"An error occurred while processing the payment: {str(e)}"


# VALIDATION ✔
@transaction.atomic
def create_misc_loan(destination_account, misc_loan_pk, reason, amount):
    try:
        account = destination_account
        account.balance += amount
        account.save()

        loan = MiscLoan.objects.get(pk=misc_loan_pk)

        Ledger.objects.create(
            transaction_type="MISC_LOAN_CREATE",
            project=None,
            amount=amount,
            source_content_type=ContentType.objects.get_for_model(loan),
            source_object_id=loan.pk,
            destination_content_type=ContentType.objects.get_for_model(account),
            destination_object_id=account.pk,
            reason=reason,
        )

        return True, "Transaction successful"

    except Exception as e:
        return False, f"An error occurred while processing the payment: {str(e)}"


# VALIDATED ✔
@transaction.atomic
def return_misc_loan(destination_account, source, reason, amount):
    try:
        # ACC Balance Instance
        source.balance -= amount
        source.save()

        # Loan Instance
        destination_account.update_remaining_amount(amount)
        destination_account.save()

        Ledger.objects.create(
            transaction_type="MISC_LOAN_RETURN",
            project=None,
            amount=amount,
            source_content_type=ContentType.objects.get_for_model(source),
            source_object_id=source.pk,
            destination_content_type=ContentType.objects.get_for_model(
                destination_account
            ),
            destination_object_id=destination_account.pk,
            reason=reason,
        )

        return (
            True,
            f"Loan return of {amount} form {source.account_name} was successful",
        )

    except Exception as e:
        return False, f"An error occurred while processing the payment: {str(e)}"


# VALIDATION ✔
@transaction.atomic
def add_cash_to_project(project_id, amount, reason):
    try:
        project = Project.objects.select_for_update().get(pk=project_id)
        project.project_cash += amount
        project.project_account_balance -= amount
        project.save(update_fields=["project_cash", "project_account_balance"])

        Ledger.objects.create(
            transaction_type="TRANSFER",
            project=project,
            amount=amount,
            source_content_type=ContentType.objects.get_for_model(project),
            source_object_id=project.pk,
            destination_content_type=ContentType.objects.get_for_model(project),
            destination_object_id=project.pk,
            reason=reason,
        )
        return True, "Transaction successful"
    except Exception as e:
        return False, f"An error occurred while processing the payment: {str(e)}"


# VALIDATION ✔
@transaction.atomic
def add_general_cash_in_hand(amount, source, reason):
    try:
        cashinhand = CashInHand.objects.select_for_update().first()
        cashinhand.balance += amount
        cashinhand.save()
        account = source
        account.balance -= amount
        account.save()

        Ledger.objects.create(
            transaction_type="ADD_CASH",
            amount=amount,
            source_content_type=ContentType.objects.get_for_model(source),
            source_object_id=source.pk,
            destination_content_type=ContentType.objects.get_for_model(cashinhand),
            destination_object_id=cashinhand.pk,
            reason=reason,
        )
        return True, "Transaction successful"
    except Exception as e:
        return False, f"A Fatal error occurred while processing the payment: {str(e)}"


def add_account_balance(amount, account_pk, reason):
    try:
        account = AccountBalance.objects.select_for_update().get(pk=account_pk)
        account.balance += amount
        account.save()

        Ledger.objects.create(
            transaction_type="ADD_ACC_BALANCE",
            amount=amount,
            destination_content_type=ContentType.objects.get_for_model(account),
            destination_object_id=account.pk,
            reason=reason,
        )
        return True, "Transaction successful"
    except Exception as e:
        return False, f"A Fatal error occurred while processing the payment: {str(e)}"
