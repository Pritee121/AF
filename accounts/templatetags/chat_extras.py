from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    """ Custom filter to fetch a value from a dictionary using a key """
    return dictionary.get(key, 0)  # Return 0 if key not found
