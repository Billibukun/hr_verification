from django import template
from django.db import models

register = template.Library()

@register.filter
def get_visible_fields(model):
    if isinstance(model, models.Model):
        return [field for field in model._meta.get_fields() if not field.is_relation or field.one_to_one or (field.many_to_one and field.related_model)]
    return []

@register.filter
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(value, str(arg)):
        return getattr(value, str(arg))
    elif hasattr(value, 'get'):
        return value.get(arg)
    else:
        return None

@register.filter
def default_if_none(value, default):
    return value if value is not None else default

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def replace_underscores(value):
    return value.replace('_', ' ')

@register.filter
def get_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return None
    
@register.filter(name='class_name')
def class_name(value):
    return value.__class__.__name__