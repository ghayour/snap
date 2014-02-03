#coding= utf-8
import os
import base64

from django import template

register = template.Library()


@register.filter
def filename(value):
    filename = os.path.basename(value.file.name).split('.')[0]
    try:
        x = unicode(base64.urlsafe_b64decode(str(filename)))
        return x

    except Exception:
        # TODO: check this!
        x = unicode(filename)
        return x
