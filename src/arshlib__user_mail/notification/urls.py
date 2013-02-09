# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('cms.cms.notification.views',
    url(r'^$', 'show_notifications', name='notifications/show'),
    url(r'^(?P<notification_id>\d+)/description/$', 'show_description', name='notifications/description'),
    url(r'^create/$', 'notification_create', name='notifications/create'),
)