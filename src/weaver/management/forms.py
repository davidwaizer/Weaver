#coding=utf-8
from datetime import date
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from management.models import ServerImage, Site, Server
from boto.ec2.connection import EC2Connection

from utils import forms


class ServerImageForm(forms.ModelForm):
    
    class Meta:
        model = ServerImage
        exclude = ['ami_id',]


class SiteForm(forms.ModelForm):
    
    class Meta:
        model = Site

        
class ServerForm(forms.ModelForm):
    
    class Meta:
        model = Server




