# -*- coding: utf-8 -*-
import urllib

from django.core.urlresolvers import reverse
from django.http import Http404


def get_subclass_or_404(model, **kwargs):
    try:
        return model.objects.select_subclasses().get(**kwargs)
    except model.DoesNotExist:
        raise Http404()


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.urlencode(get)
    return url


def get_mime_type(filename):
    ext = filename[filename.rindex('.') + 1:]
    if ext == 'js':
        mime_type = 'text/javascript'
    elif ext == 'css':
        mime_type = 'text/css'
    elif ext in ['htm', 'html']:
        mime_type = 'text/html'
    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'tif', 'svg']:
        trans = {'jpg': 'jpeg',
                 'ico': 'image/vnd.microsoft.icon',
                 'tif': 'tiff',
                 'svg': 'svg+xml'}
        mime_type = 'image/'
        if ext in trans:
            mime_type += trans[ext]
        else:
            mime_type += ext
    else:
        return None
    return mime_type
