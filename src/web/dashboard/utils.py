from django.db.models import Sum, Q
from django.db.models.functions import ExtractMonth
from src.services.transaction.models import Ledger

from django.contrib.contenttypes.models import ContentType
from src.services.transaction.models import Ledger


def get_monthly_income_expense(project_id=None):

    transactions = Ledger.objects.all()
    if project_id:
        transactions = Ledger.objects.filter(project_id=project_id)

    monthly_income = (
        transactions.filter(transaction_type="INVOICE_PAYMENT")
        .annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    monthly_expense = (
        transactions.filter(transaction_type__in=["CREATE_EXPENSE", "RETURN_LOAN"])
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


def ledger_filter(transaction_type=None, destination=None, source=None):
    """
    Utility to filter Ledger objects by source, destination, and transaction type.

    Args:
        transaction_type (str, optional): The transaction type to filter by.
        destination (models.Model, optional): The destination object instance.
        source (models.Model, optional): The source object instance.

    Returns:
        QuerySet: Filtered Ledger objects.
    """
    # Inclusive OR
    if source and destination:
        source_content_type = ContentType.objects.get_for_model(source)
        destination_content_type = ContentType.objects.get_for_model(destination)
        query = Q(
            Q(source_content_type=source_content_type, source_object_id=source.pk)
            | Q(
                destination_content_type=destination_content_type,
                destination_object_id=destination.pk,
            )
        )
        if transaction_type:
            query &= Q(transaction_type=transaction_type)
        return Ledger.objects.filter(query)
    elif source:
        source_content_type = ContentType.objects.get_for_model(source)
        kwargs = {
            "source_content_type": source_content_type,
            "source_object_id": source.pk,
        }
        if transaction_type:
            kwargs["transaction_type"] = transaction_type
        return Ledger.objects.filter(**kwargs)
    elif destination:
        destination_content_type = ContentType.objects.get_for_model(destination)
        kwargs = {
            "destination_content_type": destination_content_type,
            "destination_object_id": destination.pk,
        }
        if transaction_type:
            kwargs["transaction_type"] = transaction_type
        return Ledger.objects.filter(**kwargs)
    else:
        raise ValueError("At least one of 'source' or 'destination' must be provided.")


def capitalize_and_replace_currency(value):
    """
    Capitalizes the first letter of the string and replaces currency-related
    phrases with "rupees" or "rupee" appropriately.

    Args:
        value (str): The string to be transformed.

    Returns:
        str: The transformed string.
    """
    # Capitalize the first letter of the string
    value = value.strip().capitalize()

    # Replace specific phrases for cents
    replacements = {
        "euro, zero cents": "rupees",
        "euro, one cent": "rupee",
        "euro,": "rupees,",
        "euros, zero cents": "rupees",
        "euros, one cent": "rupee",
        "euros,": "rupees,",
        "cent": "",
        "cents": "",
    }

    # Perform replacements
    for old, new in replacements.items():
        value = value.replace(old, new)

    # Additional clean-up (if needed)
    value = value.strip()
    if "and rupee" in value:
        value = value.replace("and rupee", "and one rupee")
    elif "and rupees" in value:
        value = value.replace("and rupees", "and zero rupees")

    # Return the modified string
    return value
