#coding=utf-8
from datetime import date
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from management.models import ServerConfiguration, Site
from boto.ec2.connection import EC2Connection

from utils import forms

class ServerConfigurationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
            super(ServerConfigurationForm, self).__init__(*args, **kwargs)
            instance = getattr(self, 'instance', None)
            if instance and instance.id:
                self.fields['base_image_architecture'].widget.attrs['disabled'] = 'disabled'
                self.fields['base_image_name'].widget.attrs['disabled'] = 'disabled'
                
    
    def clean(self):
        cleaned_data = self.cleaned_data
        base_image = cleaned_data.get("base_image")
        
        # Make sure its an actual image.
        try:
            conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
            ami = conn.get_image(base_image)
            if ami.state <> 'available':
                msg = _(u"The AMI image you entered is not available.")
                self._errors["base_image"] = self.error_class([msg])
                del cleaned_data["base_image"]    
            
        except:
            msg = _(u"The AMI image you entered does not exist.")
            self._errors["base_image"] = self.error_class([msg])
            del cleaned_data["base_image"]
        
        return cleaned_data
    
    
    class Meta:
        model = ServerConfiguration


class SiteForm(forms.ModelForm):
    
    class Meta:
        model = Site




