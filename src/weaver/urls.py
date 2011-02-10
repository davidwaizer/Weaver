from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    url(r'^', include('core.urls', namespace='core', app_name='core')),
    url(r'^provisioning/', include('provisioning.urls', namespace='ideas', app_name='ideas')),
)

