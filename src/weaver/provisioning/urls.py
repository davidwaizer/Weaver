#coding=utf-8

from django.contrib.auth.views import password_change, password_reset
from django.conf.urls.defaults import *
from django.utils.http import urlquote


from provisioning import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	
	url(r'^configurations/$', views.serverconfiguration_index, name='serverconfiguration-index'),
	url(r'^configurations/add/$', views.serverconfiguration_add, name='serverconfiguration-add'),
	#url(r'^configurations/(?P<config_name>[-\w]+)/$', views.serverconfiguration_view, name='serverconfiguration-view'),
	url(r'^configurations/(?P<config_name>[-\w]+)/edit/$', views.serverconfiguration_edit, name='serverconfiguration-edit'),
	url(r'^configurations/(?P<config_name>[-\w]+)/delete/$', views.serverconfiguration_delete, name='serverconfiguration-delete'),

	url(r'^key-pairs/$', views.keypairs_index, name='keypairs-index'),
	
	url(r'^sites/$', views.site_index, name='site-index'),	
	url(r'^sites/add/$', views.site_add, name='site-add'),
	url(r'^sites/(?P<site_slug>[-\w]+)/edit/$', views.site_edit, name='site-edit'),
	url(r'^sites/(?P<site_slug>[-\w]+)/delete/$', views.site_delete, name='site-delete'),

)