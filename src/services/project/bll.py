from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from src.services.assets.models import CashInHand, AccountBalance
from src.services.expense.models import Expense
from src.services.invoice.models import Invoice
from src.services.loan.models import Loan, Lender
from src.services.project.models import Project
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
        source_content_type=ContentType.objects.get_for_model(project),
        source_object_id=project.pk,
        destination_content_type=ContentType.objects.get_for_model(account),
        destination_object_id=account.pk,
        reason=reason,
    )


# VALIDATION ✔
@transaction.atomic
def add_loan_to_project(project_id, amount, source, reason):
    project = Project.objects.select_for_update().get(pk=project_id)
    project.project_account_balance += amount
    project.save(update_fields=["project_account_balance"])

    lender = Lender.objects.get(pk=source.pk)

    Ledger.objects.create(
        transaction_type="CREATE_LOAN",
        project=project,
        amount=amount,
        source_content_type=ContentType.objects.get_for_model(lender),
        source_object_id=lender.pk,
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
    Expense.objects.create(
        project=project,
        description="Loan Return",
        amount=amount,
        budget_source="Project Account Balance",
        category=None,
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
        reason=reason,
    )

# VALIDATION ✔
@transaction.atomic
def create_expense_calculations(project_id, amount, budget_source, vendor_pk, reason):
    project = Project.objects.select_for_update().get(pk=project_id)

    if budget_source == "CASH":
        project.project_cash -= amount

    elif budget_source == "ACC":
        project.project_account_balance -= amount

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
        reason=reason,
    )


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


@transaction.atomic
def process_invoice_payment(invoice_id, destination, amount, account_id=None):
    try:
        invoice = Invoice.objects.select_for_update().get(pk=invoice_id)
        invoice.status = "PAID"
        invoice.save(update_fields=["status"])

        if account_id:
            account = AccountBalance.objects.select_for_update().get(pk=account_id)

        ledger_reason = f"Payment for Invoice"

        if destination == "account" and account:
            account.balance += amount
            account.save(update_fields=["balance"])

        Ledger.objects.create(
            transaction_type="INVOICE_PAYMENT",
            project=invoice.project,
            amount=amount,
            source=f"Invoice Paid: {invoice.client_name} ({invoice.pk})",
            destination=f"Wallet: {account.account_name} ({account.pk})",
            reason=ledger_reason,
        )

        return True, "Invoice successfully paid and funds transferred."

    except Exception as e:
        # Handle unexpected errors
        return False, f"An error occurred while processing the payment: {str(e)}"


@transaction.atomic
def create_journal_expense_calculations(
    category, reason, destination, amount, source, account_pk=None
):
    """
    Creates a ledger entry for a journal expense.

    :param category: The category of the expense
    :param reason: The reason for the expense
    :param destination: The vendor id to which the expense is made
    :param amount: The amount of the expense
    :param source: The source of the expense (CASH or ACC)
    :param account_pk: The account id from which the expense is made (if source is ACC)
    :return: A tuple containing a boolean indicating success and a message
    """
    try:
        # Update the account/cash balance
        if source == "ACC":
            account = AccountBalance.objects.select_for_update().get(pk=account_pk)
            account.balance -= amount
            account.save(update_fields=["balance"])
        else:
            cashinhand = CashInHand.objects.first()
            cashinhand.balance -= amount
            cashinhand.save(update_fields=["balance"])

        # Update the vendor's total expense
        if destination:
            vendor = Vendor.objects.get(pk=destination)
            vendor.total_expense += amount
            vendor.save(update_fields=["total_expense"])

        else:
            vendor = None

        # Create a ledger entry after updating the account/cash balance
        Ledger.objects.create(
            transaction_type="MISC_EXPENSE",
            amount=amount,
            source=(
                f"Wallet: {account.account_name} ({account.pk})"
                if source == "ACC"
                else f"Wallet: Cash In Hand ({cashinhand.pk})"
            ),
            destination=(f"Vendor: {vendor.name} ({vendor.pk})" if vendor else f"None"),
            reason=reason,
            category=f"{category.name} ({category.pk})",
        )
        return True, "Journal Entry Successfully created"

    except Exception as e:
        return False, f"An error occurred while processing the payment: {str(e)}"


@transaction.atomic
def create_misc_loan(destination_account, source, reason, amount):
    try:
        var = destination_account.balance + amount
        destination_account.save()

        lender = Lender.objects.get(pk=source)

        Ledger.objects.create(
            transaction_type="MISC_LOAN_CREATE",
            project=None,
            amount=amount,
            source=f"Loan: {lender.name} ({lender.pk})",
            destination=f"Wallet: {destination_account.account_name} ({destination_account.pk})",
            reason=reason,
        )

        return True, "Transaction successful"

    except Exception as e:
        return False, f"An error occurred while processing the payment: {str(e)}"


@transaction.atomic
def return_misc_loan(destination_account, source, reason, amount):
    try:
        source.balance -= amount
        source.save()

        destination_account.update_remaining_amount(amount)
        destination_account.save()

        Ledger.objects.create(
            transaction_type="MISC_LOAN_RETURN",
            project=None,
            amount=amount,
            source=f"Wallet: {source.account_name} ({source.pk})",
            destination=f"Lender: {destination_account.lender.name} ({destination_account.pk})",
            reason=reason,
        )

        return True, "Transaction successful"

    except Exception as e:
        return False, f"An error occurred while processing the payment: {str(e)}"
