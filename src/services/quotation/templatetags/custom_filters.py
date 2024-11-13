# custom_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def capitalize_and_replace(value):
    # Capitalize the first letter of the string
    value = value.capitalize()

    # Replace "euro, zero cents" with "rupees"
    value = value.replace("euro, zero cents", "rupees")

    return value