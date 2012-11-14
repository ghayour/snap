# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404

from rezgh.places.models import Shop

from arsh.simple_request.models import SimpleRequest



@permission_required('accounts.confirm')
def check_confirming(request, url):
    """
        :type request: django.http.HttpRequest
        :rtype: django.http.HttpResponse
    """
    for simple_request in SimpleRequest.objects.filter(url_accept__endswith=url):
        simple_request.request_object.accept()
    for simple_request in SimpleRequest.objects.filter(url_reject__endswith=url):
        simple_request.request_object.reject()
    if request.is_ajax():
        return HttpResponse('OK')
    referrer = request.META.get('HTTP_REFERER', '')
    if not referrer or not referrer.startswith(settings.SITE_URL):
        referrer = reverse('mail/home')
    return HttpResponseRedirect(referrer)

@permission_required('accounts.confirm')
def direct_eval(request, app, model, id, action):
    ct = get_object_or_404(ContentType, app_label=app, model=model)
    object = get_object_or_404(ct.model_class(), id=id)
    if action == 'accept':
        object.accepted = True
    elif action == 'reject':
        object.accepted = False
    elif action == 'clear':
        object.accepted = None
    else:
        raise Http404('No such action: ' + action)
    object.save()
    return HttpResponse('OK')


@permission_required('accounts.confirm')
def confirming_show(request):
    shops = SimpleRequest.objects.filter(status=None)
    return render_to_response('places/check_new_shop_request.html', {'shops': shops})


@permission_required('accounts.confirm')
def reports_status(request):
    requests = SimpleRequest.objects.select_related().filter().order_by('-created_at')
    return render_to_response('places/reports_status.html', {'requests': requests, 'handle': request.GET.get('handle', '')})