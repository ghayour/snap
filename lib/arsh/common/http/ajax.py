# -*- coding: utf-8 -*-
from functools import wraps
from django.http import HttpResponse
from django.utils import simplejson


def json_response(array, status=200):
    return HttpResponse(simplejson.dumps(array), mimetype='application/json', status=status)


def ajax_view(view):
    @wraps(view)
    def json_view(*args, **kwargs):
        result = view(*args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        return json_response(result)

    return json_view


def xml_response(xml):
    return HttpResponse(xml, mimetype='application/xml')


def png_response(image):
    """
        :type image: Image.Image
        :rtype: HttpResponse
    """
    response = HttpResponse(mimetype="image/png")
    image.save(response, "PNG")
    return response
