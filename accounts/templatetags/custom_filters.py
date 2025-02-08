from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    """Divides the value by the argument and rounds to 2 decimal places."""
    try:
        return round(float(value) / float(arg), 2)
    except (ValueError, ZeroDivisionError):
        return 0
