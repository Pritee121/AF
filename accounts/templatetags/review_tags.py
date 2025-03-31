from django import template

register = template.Library()

@register.filter
def average(queryset, field):
    values = [getattr(obj, field, 0) for obj in queryset if getattr(obj, field, None) is not None]
    return round(sum(values) / len(values), 1) if values else 0

@register.filter
def repeat(value, count):
    return value * int(count)
