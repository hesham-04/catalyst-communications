from django.db import transaction
from django.apps import apps
from .exceptions import TransactionError


@transaction.atomic
def budget_assign(source, destination, amount, **kwargs):
    """
    Handles the BUDGET_ASSIGN transaction type.
    - Source is ACC Balance; return to the source.
    - Destination is the Project; remove from the project.
    """
    if destination.project_account_balance < amount:
        raise TransactionError(
            f"Insufficient balance in {destination.project_name} account.",
            details={"source": source, "amount": amount},
        )
    else:
        source.balance += amount
        destination.project_account_balance -= amount
        source.save()
        destination.save()


@transaction.atomic
def transfer(source, amount, **kwargs):
    """
    Handles the TRANSFER transaction type.
    - Source and destination are projects.
    - Remove from destination (Project Cash) and add to source (Project ACC Balance).
    """
    if source.project_cash < amount:
        raise TransactionError(
            f"Insufficient cash in {source.project_name} account.",
            details={"source": source, "amount": amount},
        )
    else:
        source.project_cash -= amount
        source.project_account_balance += amount
        source.save()


@transaction.atomic
def create_loan(source, destination, amount, **kwargs):
    """
    Handles the CREATE_LOAN transaction type.
    - Delete the source instance.
    - Remove the amount from the destination's project account balance.
    """
    if destination.project_account_balance < amount:
        raise TransactionError(
            f"Insufficient balance in {destination.project_name} account.",
            details={"source": source, "amount": amount},
        )
    else:
        source.delete()
        destination.project_account_balance -= amount
        destination.save()


@transaction.atomic
def return_loan(source, destination, amount, **kwargs):
    """
    Handles the RETURN_LOAN transaction type.
    - Increase the loan's remaining amount.
    - Add the amount back to the project's account balance.
    - Delete the associated expense instance.
    """
    # No need for exception.
    destination.remaining_amount += amount
    source.project_account_balance += amount
    source.save()
    destination.save()
    expense = kwargs.get("expense")
    print("Expense: ", expense)
    expense.delete()


@transaction.atomic
def misc_loan_create(source, destination, amount, **kwargs):
    """
    Handles the MISC_LOAN_CREATE transaction type.
    - Remove the amount from the account balance.
    - Delete the source (loan) instance.
    """
    if source.balance < amount:
        raise TransactionError(
            f"Insufficient balance in {source.project_name} account.",
            details={"source": source, "amount": amount},
        )
    else:
        destination.balance -= amount
        source.delete()
        destination.save()


@transaction.atomic
def misc_loan_return(source, destination, amount, **kwargs):
    """
    Handles the MISC_LOAN_RETURN transaction type.
    - Increase the loan's remaining amount.
    - Add the amount back to the source's account balance.
    """
    # No need for exception.
    destination.remaining_amount += amount
    source.balance += amount
    source.save()
    destination.save()


@transaction.atomic
def create_expense(source, amount, **kwargs):
    """
    Handles the CREATE_EXPENSE transaction type.
    - Add the amount back to the project's account balance.
    - Delete the associated expense instance.
    """
    # No need for Exceptions
    source.project_account_balance += amount
    source.save()
    expense = kwargs.get("expense")
    expense.delete()


@transaction.atomic
def misc_expense(source, amount, **kwargs):
    """
    Handles the MISC_EXPENSE transaction type.
    - Add the amount back to the source's balance.
    - Delete the associated misc expense instance.
    """
    # No need for Exceptions
    source.balance += amount
    source.save()
    expense = kwargs.get("misc_expense")
    expense.delete()


@transaction.atomic
def add_cash(source, destination, amount, **kwargs):
    """
    Handles the ADD_CASH transaction type.
    - Transfer cash from the destination to the source.
    """
    if destination.balance < amount:
        raise TransactionError(
            f"Insufficient balance in {destination.project_name} account.",
            details={"source": source, "amount": amount},
        )
    else:
        source.balance += amount
        source.save()
        destination.balance -= amount
        destination.save()


@transaction.atomic
def invoice_payment(source, destination, amount, **kwargs):
    """
    Placeholder for INVOICE_PAYMENT transaction type.
    """
    if destination.balance < amount:
        raise TransactionError(
            f"Insufficient balance in {destination.account_name} account.",
            details={"source": source, "amount": amount},
        )
    else:
        source.status = "PENDING"
        source.save()
        destination.balance -= amount
        destination.save()


@transaction.atomic
def add_acc_balance(source, destination, **kwargs):
    """
    Placeholder for ADD_ACC_BALANCE transaction type.
    """
    pass  # Implementation needed


# Map transaction types to their handlers
TRANSACTION_HANDLERS = {
    "BUDGET_ASSIGN": budget_assign,
    "TRANSFER": transfer,
    "CREATE_LOAN": create_loan,
    "RETURN_LOAN": return_loan,  # KWARGS
    "MISC_LOAN_CREATE": misc_loan_create,
    "MISC_LOAN_RETURN": misc_loan_return,
    "CREATE_EXPENSE": create_expense,  # KWARGS
    "MISC_EXPENSE": misc_expense,  # KWARGS
    "ADD_CASH": add_cash,
    "INVOICE_PAYMENT": invoice_payment,
    "ADD_ACC_BALANCE": add_acc_balance,
}
