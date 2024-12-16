from django.utils.text import slugify


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
