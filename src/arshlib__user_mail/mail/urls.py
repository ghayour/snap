# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url




urlpatterns = patterns('arsh.mail.views',
    url(r'^compose$', 'compose', name='mail/compose'),
#    url(r'^addLabel/$', 'addLabel', name='mail/addLabel'),
    url(r'^search/$', 'search', name='mail/search'),

    url(r'^view/$', 'see', {'label_slug': None, 'thread_slug': None}, name='mail/home'),
    url(r'^view/archive/$', 'see', {'label_slug': None, 'thread_slug': None, 'archive': True}, name='mail/inbox_archive'),
    url(r'^view/(?P<label_slug>[a-zA-Z0-9_\.]+)/$', 'see', {'thread_slug': None}, name='mail/see_label'),
    url(r'^view/(?P<label_slug>[a-zA-Z0-9_\.]+)/archive$', 'see', {'thread_slug': None, 'archive': True}, name='mail/see_label_archive'),
    url(r'^view/(?P<label_slug>[a-zA-Z0-9_\.]+)/(?P<thread_slug>[a-zA-Z0-9_\.]+)/$', 'see', name='mail/see_thread'),
    url(r'^threads/view/(?P<thread_slug>[a-zA-Z0-9_\.]+)/$', 'see', {'label_slug': None}, name='mail/see_thread_direct'),
    url(r'^threads/(?P<thread_slug>[a-zA-Z0-9_\.]+)/mark_(?P<action>read|unread)$', 'mark_thread', name='mail/thread/mark'),

    url(r'^setup$', 'setup')
)
