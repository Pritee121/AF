from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get an item from a dictionary, return empty list if key not found."""
    if dictionary is None:
        return []  # ✅ Return empty list if dictionary is None
    return dictionary.get(key, [])  # ✅ Return empty list if key does not exist
