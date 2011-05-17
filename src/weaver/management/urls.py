#coding=utf-8

from django.contrib.auth.views import password_change, password_reset
from django.conf.urls.defaults import *
from django.utils.http import urlquote


from management import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	
	url(r'^server-images/$', views.serverimage_index, name='serverimage-index'),
	url(r'^serverimages/(?P<ami_id>[-\w]+)/manage/$', views.serverimage_manage, name='serverimage-manage'),
    
	url(r'^key-pairs/$', views.keypairs_index, name='keypairs-index'),
	
	url(r'^sites/$', views.site_index, name='site-index'),	
	url(r'^sites/add/$', views.site_add, name='site-add'),
	url(r'^sites/(?P<site_slug>[-\w]+)/edit/$', views.site_edit, name='site-edit'),
	url(r'^sites/(?P<site_slug>[-\w]+)/delete/$', views.site_delete, name='site-delete'),
    
	url(r'^servers/$', views.server_index, name='server-index'),	
	url(r'^servers/(?P<instance_id>[-\w]+)/manage/$', views.server_manage, name='server-manage'),
    
)