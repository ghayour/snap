# -*- coding: utf-8 -*-
from importlib import import_module
import re
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def server_error(request, template_name='500.html'):
    return render_to_response(template_name, context_instance=RequestContext(request))


def js_url_resolver(request):
    pname = settings.PROJECT_NAME
    js = "var SITE_URL = '%s';\narsh.dj.resolver.initialize(SITE_URL);\n" % settings.SITE_URL
    for app in settings.INSTALLED_APPS:
        if app.startswith(pname + '.'):
            try:
                m = import_module(app + '.urls')
            except ImportError:
                continue

            app_name = app[len(pname) + 1:]
            js += "arsh.dj.resolver.register_app('%s', '%s', {\n" % (app_name, app_name)
            urls = []
            for url in m.urlpatterns:
                u = url.regex.pattern
                # removing surrounding ^ and $:
                u = re.sub(r'(^\^|\$$)', '', u)
                # named parameters:
                u = re.sub(r'\(\?P<([^>]+)>[^)]+\)', r'{{\1}}', u)
                # unnamed groups: (these are converted to {{1}}, {{2}}, ...)
                rep_count = 1
                index = 1
                while rep_count > 0:
                    u, rep_count = re.subn(r'\([^){}]+\)\??', '{{%d}}' % index, u, count=1)
                    index += 1
                # optional arguments: (converting `(x)?` to `x`)
                u = re.sub(r'\(([^)]+)\)\?', r'\1', u)
                urls.append("    '%s': '%s'" % (url.name, u))
            js += ',\n'.join(urls)
            js += "\n});\n"
    return HttpResponse(js)
