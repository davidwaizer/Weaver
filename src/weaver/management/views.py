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

from management.models import ServerImage, KeyPairManager, Site, Server
from management.forms import ServerImageForm, SiteForm, ServerForm

from boto.ec2.connection import EC2Connection

def index(request):
    return render_to_response('management/index.html', {}, context_instance=RequestContext(request))


def serverimage_index(request):
    configs = ServerImage.objects.all()
    return render_to_response('management/serverimage_index.html', {'configs': configs}, context_instance=RequestContext(request))
    

def serverimage_add(request):
    form = ServerImageForm()
    
    if request.method == 'POST':
        form = ServerImageForm(request.POST)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('management:serverimage-edit', args=(config.slug,)))
    
    return render_to_response('management/serverimage_add.html', { 'form': form }, context_instance=RequestContext(request))


def serverimage_edit(request, config_name):
    config = get_object_or_404(ServerImage, slug=config_name)
    form = ServerImageForm(instance=config)
    
    if request.method == 'POST':
        form = ServerImageForm(request.POST, request.FILES, instance=config)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('management:serverimage-edit', args=(config.slug,)))
    
    return render_to_response('management/serverimage_edit.html', { 'form': form, 'config': config }, context_instance=RequestContext(request))


def serverimage_delete(request, config_name):
    config = get_object_or_404(ServerImage, slug=config_name)
    
    if request.method == 'POST':
        if request.POST.get('delete', '0') == '1':
            config.delete()
            return HttpResponseRedirect(reverse('management:serverimage-index'))
    
    return render_to_response('management/serverimage_delete.html', { 'config': config }, context_instance=RequestContext(request))


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


def server_index(request):
    servers = Server.objects.all()
    return render_to_response('management/server_index.html', { 'servers': servers }, context_instance=RequestContext(request))
    
    
def server_add(request):
    form = ServerForm()

    if request.method == 'POST':
        form = ServerForm(request.POST)
        
        if form.is_valid():
            server = form.save()
            return HttpResponseRedirect(reverse('management:server-edit', args=(server.slug,)))

    return render_to_response('management/server_add.html', { 'form': form }, context_instance=RequestContext(request))


def server_edit(request, server_slug):
    server = get_object_or_404(Server, slug=server_slug)
    form = ServerForm(instance=server)

    if request.method == 'POST':
        form = ServerForm(request.POST, request.FILES, instance=server)
        
        if form.is_valid():
            server = form.save()
            return HttpResponseRedirect(reverse('management:server-edit', args=(server.slug,)))

    return render_to_response('management/server_edit.html', { 'form': form, 'server': server }, context_instance=RequestContext(request))


def server_delete(request, server_slug):
    server = get_object_or_404(Site, slug=server_slug)
    
    if request.method == 'POST':
        if request.POST.get('delete', '0') == '1':
            server.delete()
            return HttpResponseRedirect(reverse('management:server-index'))
    
    return render_to_response('management/server_delete.html', { 'server': server }, context_instance=RequestContext(request))

