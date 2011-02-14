#coding=utf-8

from django import http
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext

from management.models import ServerConfiguration, KeyPairManager, Site
from management.forms import ServerConfigurationForm, SiteForm

from boto.ec2.connection import EC2Connection

def index(request):
    return render_to_response('management/index.html', {}, context_instance=RequestContext(request))


def serverconfiguration_index(request):
    configs = ServerConfiguration.objects.all()
    return render_to_response('management/serverconfiguration_index.html', {'configs': configs}, context_instance=RequestContext(request))
    

def serverconfiguration_add(request):
    form = ServerConfigurationForm()
    
    if request.method == 'POST':
        form = ServerConfigurationForm(request.POST)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('management:serverconfiguration-edit', args=(config.slug,)))
    
    return render_to_response('management/serverconfiguration_add.html', { 'form': form }, context_instance=RequestContext(request))


def serverconfiguration_edit(request, config_name):
    config = get_object_or_404(ServerConfiguration, slug=config_name)
    form = ServerConfigurationForm(instance=config)
    
    if request.method == 'POST':
        form = ServerConfigurationForm(request.POST, request.FILES, instance=config)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('management:serverconfiguration-edit', args=(config.slug,)))
    
    return render_to_response('management/serverconfiguration_edit.html', { 'form': form, 'config': config }, context_instance=RequestContext(request))


def serverconfiguration_delete(request, config_name):
    config = get_object_or_404(ServerConfiguration, slug=config_name)
    
    if request.method == 'POST':
        if request.POST.get('delete', '0') == '1':
            config.delete()
            return HttpResponseRedirect(reverse('management:serverconfiguration-index'))
    
    return render_to_response('management/serverconfiguration_delete.html', { 'config': config }, context_instance=RequestContext(request))


def keypairs_index(request):
    ec2_keypairs = KeyPairManager.get_ec2_public_keys()
    local_keypairs = KeyPairManager.get_local_private_keys()
    return render_to_response('management/keypairs_index.html', { 'ec2_keypairs': ec2_keypairs, 'local_keypairs': local_keypairs }, context_instance=RequestContext(request))
    
    
def site_index(request):
    sites = Site.objects.all()
    return render_to_response('management/site_index.html', { 'sites': sites }, context_instance=RequestContext(request))
        

def site_add(request):
    form = SiteForm()

    if request.method == 'POST':
        form = SiteForm(request.POST)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('management:site-edit', args=(config.slug,)))
    
    return render_to_response('management/site_add.html', { 'form': form }, context_instance=RequestContext(request))


def site_edit(request, site_slug):
    site = get_object_or_404(Site, slug=site_slug)
    form = SiteForm(instance=site)

    if request.method == 'POST':
        form = SiteForm(request.POST, request.FILES, instance=site)

        if form.is_valid():
            site = form.save()
            return HttpResponseRedirect(reverse('management:site-edit', args=(site.slug,)))

    return render_to_response('management/site_edit.html', { 'form': form, 'site': site }, context_instance=RequestContext(request))


def site_delete(request, site_slug):
    site = get_object_or_404(Site, slug=site_slug)

    if request.method == 'POST':
        if request.POST.get('delete', '0') == '1':
            site.delete()
            return HttpResponseRedirect(reverse('management:site-index'))

    return render_to_response('management/site_delete.html', { 'site': site }, context_instance=RequestContext(request))
