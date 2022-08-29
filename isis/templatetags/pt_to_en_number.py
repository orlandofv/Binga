from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def pt_to_en(value):
    print(value)
    value = float(f"{value}".replace(",","."))
    print(value, type(value))
    return value