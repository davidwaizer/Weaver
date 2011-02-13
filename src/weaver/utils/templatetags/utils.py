import copy
from datetime import date

from django.template import Library
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse
from django.utils.safestring import SafeUnicode, SafeString

#from django.utils.html import escape
#from django.template import Library, Node
#from django.utils.translation import ugettext as _


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

@register.filter
def is_active(request, url):
	url = reverse(url)
	if request == None:
		return False
	is_active = False	
	current_url = request.path
	if url != SafeUnicode('/'):
		is_active = SafeUnicode(current_url).startswith(url)
	else:
		is_active = url == SafeUnicode(current_url)

	return is_active

@register.filter
def subnav_is_active(request, url):
	url = reverse(url)
	if request == None:
		return False
	is_active = False
	current_url = request.path
	is_active = url == SafeUnicode(current_url)
	return is_active