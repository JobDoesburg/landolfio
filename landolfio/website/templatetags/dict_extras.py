from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter to get an item from a dictionary using a variable key."""
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

@register.filter
def getlist(querydict, key):
    """Template filter to get a list of values from a QueryDict using a variable key."""
    if querydict is None:
        return []
    try:
        return querydict.getlist(key)
    except (AttributeError, TypeError):
        return []

@register.filter
def value_in_list(value, value_list):
    """Template filter to check if a value is in a list."""
    if value_list is None:
        return False
    try:
        return value in value_list
    except (TypeError, AttributeError):
        return False