# -*- coding: utf-8 -*-
from django.conf.urls.defaults             import patterns, url




urlpatterns = patterns('arsh.simple_request.views',
    #url('new_shop_request/$', 'add_new_shop', name='add_new_shop'),
    #url('confirm_list/$', 'confirming_show', name='confirming_show'),
    url('^eval/(?P<url>.+)', 'check_confirming', name='simple_request/eval'),
    url('^direct-eval/(?P<app>[^/]+)/(?P<model>[^/]+)/(?P<id>\d+)/(?P<action>[^/]+)', 'direct_eval', name='simple_request/direct_eval'),
    url('^reports/status$', 'reports_status', name='simple_request/reports/status'),
)
