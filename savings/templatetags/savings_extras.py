from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        result = float(value) * float(arg)
        return min(result, 100)  # Cap at 100%
    except (ValueError, TypeError):
        return 0  # Return 0 instead of empty string 