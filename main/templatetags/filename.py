import os

from django import template


register = template.Library()

@register.filter
def filename(value):
    try:
        return os.path.basename(value.file.name)
    except AttributeError:
        return "No software uploaded"
