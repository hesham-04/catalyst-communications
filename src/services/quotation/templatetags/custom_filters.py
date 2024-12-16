# custom_filters.py
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""

    # return float(value) * float(arg)


@register.filter
def apply_tax(total_amount, percent_tax):
    try:
        tax_amount = (total_amount * percent_tax) / 100
        total_with_tax = total_amount + tax_amount
        return round(total_with_tax, 2)  # round to 2 decimal places if needed
    except (TypeError, ValueError):
        return total_amount  # return the original amount if there's an error
