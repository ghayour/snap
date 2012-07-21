# -*- coding: utf-8 -*-

from django.conf                           import settings
from django.contrib                        import admin
from django.conf.urls.defaults             import patterns, include, url




admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^sample/', include('.sample.urls')),
)

if settings.SERVE_STATIC_FILES:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.STATIC_ROOT, }
        )
    )
