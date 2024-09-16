# custom_filters.py

from django import template
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def ordinal(value):
    if 10 <= (value % 100) <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
    return suffix

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Add a CSS class to a form field widget.
    """
    value.field.widget.attrs['class'] = value.field.widget.attrs.get('class', '') + ' ' + css_class
    return value