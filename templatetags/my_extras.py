#coding= utf-8
import os
from django import template

register = template.Library()

@register.filter
def filename(value):
    import base64
    filename=os.path.basename(value.file.name).split('.')[0]
    return unicode(base64.urlsafe_b64decode(str(filename)), 'utf-8')
