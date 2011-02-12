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


def index(request):
    return render_to_response('provisioning/index.html', {}, context_instance=RequestContext(request))


def serverconfiguration_index(request):
    return render_to_response('provisioning/serverconfiguration_index.html', {}, context_instance=RequestContext(request))
    

def serverconfiguration_add(request):
    return render_to_response('provisioning/serverconfiguration_add.html', {}, context_instance=RequestContext(request))


def serverconfiguration_edit(request, config_id):
    return render_to_response('provisioning/serverconfiguration_edit.html', {}, context_instance=RequestContext(request))

def serverconfiguration_view(request, config_name):
    config = { 'name': 'Apache2',  }
    return render_to_response('provisioning/serverconfiguration_view.html', { 'config': config }, context_instance=RequestContext(request))
