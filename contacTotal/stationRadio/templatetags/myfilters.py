from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Divide el string usando el delimitador proporcionado."""
    if not value:
        return []
    parts = value.split(delimiter)
    if len(parts) == 1:
        return [value]
    return parts

@register.filter
def index(sequence, position):
    """Accede a un elemento en una posición del array."""
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return None
