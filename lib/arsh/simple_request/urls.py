# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('arsh.simple_request.views',
                       url('^eval/(?P<url>.+)', 'check_confirming', name='simple_request/eval'),
                       url('^direct-eval/(?P<app>[^/]+)/(?P<model>[^/]+)/(?P<pk>\d+)/(?P<action>[^/]+)', 'direct_eval',
                           name='simple_request/direct_eval'),
)