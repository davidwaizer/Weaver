from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    url(r'^', include('core.urls', namespace='core', app_name='core')),
    url(r'^', include('management.urls', namespace='management', app_name='management')),
    
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    
)

