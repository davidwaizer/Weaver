from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe



def index(request):
    return render_to_response('core/index.html', {}, RequestContext(request))
    

def login(request):
    return render_to_response('core/login.html', {}, RequestContext(request))
    

def logout(request):
    return render_to_response('core/logout.html', {}, RequestContext(request))