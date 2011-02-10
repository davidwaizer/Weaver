import copy
from datetime import date

from django.template import Library
from django.utils.datastructures import SortedDict

register = Library()

@register.filter
def formfields(form, fields):
    fields = [f.strip() for f in fields.split(',')]
    new_fields = []
    for name in fields:
        field = form.fields.get(name)
        if field:
            new_fields.append((name, field))
    new_form = copy.copy(form)
    new_form.fields = SortedDict(new_fields)
    return new_form

