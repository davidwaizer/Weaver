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

from provisioning.models import ServerConfiguration, KeyPairManager
from provisioning.forms import ServerConfigurationForm

from boto.ec2.connection import EC2Connection

def index(request):
    return render_to_response('provisioning/index.html', {}, context_instance=RequestContext(request))


def serverconfiguration_index(request):
    configs = ServerConfiguration.objects.all()
    return render_to_response('provisioning/serverconfiguration_index.html', {'configs': configs}, context_instance=RequestContext(request))
    

def serverconfiguration_add(request):
    form = ServerConfigurationForm()
    
    if request.method == 'POST':
        form = ServerConfigurationForm(request.POST)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('provisioning:serverconfiguration-edit', args=(config.slug,)))
    
    return render_to_response('provisioning/serverconfiguration_add.html', { 'form': form }, context_instance=RequestContext(request))


def serverconfiguration_edit(request, config_name):
    config = get_object_or_404(ServerConfiguration, slug=config_name)
    form = ServerConfigurationForm(instance=config)
    
    if request.method == 'POST':
        form = ServerConfigurationForm(request.POST, request.FILES, instance=config)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('provisioning:serverconfiguration-edit', args=(config.slug,)))
    
    return render_to_response('provisioning/serverconfiguration_edit.html', { 'form': form, 'config': config }, context_instance=RequestContext(request))

def serverconfiguration_view(request, config_name):
    config = { 'name': 'Apache2',  }
    return render_to_response('provisioning/serverconfiguration_view.html', { 'config': config }, context_instance=RequestContext(request))


def keypairs_index(request):
    ec2_keypairs = KeyPairManager.get_ec2_public_keys()
    local_keypairs = KeyPairManager.get_local_private_keys()
    return render_to_response('provisioning/keypairs_index.html', { 'ec2_keypairs': ec2_keypairs, 'local_keypairs': local_keypairs }, context_instance=RequestContext(request))
    