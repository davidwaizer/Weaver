#coding=utf-8

from django.contrib.auth.views import password_change, password_reset
from django.conf.urls.defaults import *
from django.utils.http import urlquote


from management import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	
	url(r'^configurations/$', views.serverimage_index, name='serverimage-index'),
	url(r'^configurations/add/$', views.serverimage_add, name='serverimage-add'),
	#url(r'^configurations/(?P<config_name>[-\w]+)/$', views.serverimage_view, name='serverimage-view'),
	url(r'^configurations/(?P<config_name>[-\w]+)/edit/$', views.serverimage_edit, name='serverimage-edit'),
	url(r'^configurations/(?P<config_name>[-\w]+)/delete/$', views.serverimage_delete, name='serverimage-delete'),

	url(r'^key-pairs/$', views.keypairs_index, name='keypairs-index'),
	
	url(r'^sites/$', views.site_index, name='site-index'),	
	url(r'^sites/add/$', views.site_add, name='site-add'),
	url(r'^sites/(?P<site_slug>[-\w]+)/edit/$', views.site_edit, name='site-edit'),
	url(r'^sites/(?P<site_slug>[-\w]+)/delete/$', views.site_delete, name='site-delete'),

)