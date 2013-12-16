#coding= utf-8
import os
import base64

from django import template

register = template.Library()


@register.filter
def filename(value):
    filename = os.path.basename(value.file.name).split('.')[0]
    try:
        return unicode(base64.urlsafe_b64decode(str(filename)))
    except TypeError:
        # TODO: check this!
        return filename
