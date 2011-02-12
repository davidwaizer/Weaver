#coding=utf-8
from datetime import date
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from provisioning.models import ServerConfiguration

from utils import forms

class ServerConfigurationForm(forms.ModelForm):
    class Meta:
        model = ServerConfiguration

