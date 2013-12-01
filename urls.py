# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from django.conf import settings
from django.contrib.auth.views import login, logout

urlpatterns = patterns('arsh.user_mail.views',
    url(r'^compose$', 'compose', name='mail/compose'),
    url(r'^search/$', 'search', name='mail/search'),
    url(r'^view/$', 'see', {'label_slug': None, 'thread_slug': None}, name='mail/home'),
    url(r'^view/archive/$', 'see', {'label_slug': None, 'thread_slug': None, 'archive': True},
        name='mail/inbox_archive'),
    url(r'^view/(?P<label_slug>[a-zA-Z0-9_\.]+)/$', 'see', {'thread_slug': None}, name='mail/see_label'),
    url(r'^view/(?P<label_slug>[a-zA-Z0-9_\.]+)/archive$', 'see', {'thread_slug': None, 'archive': True},
        name='mail/see_label_archive'),
    url(r'^view/(?P<label_slug>[a-zA-Z0-9_\.]+)/(?P<thread_slug>[a-zA-Z0-9_\.]+)/$', 'see', name='mail/see_thread'),
    url(r'^threads/view/(?P<thread_slug>[a-zA-Z0-9_\.]+)/$', 'see', {'label_slug': None}, name='mail/see_thread_direct')
    ,
    url(r'^threads/(?P<thread_slug>[a-zA-Z0-9_\.]+)/mark_(?P<action>read|unread)$', 'mark_thread',
        name='mail/thread/mark'),
    url(r'^mark-threads', 'ajax_mark_thread', name='mail/mark_thread'),
    url(r'^setup$', 'setup'),
    url(r'^unread/mails$', 'get_total_unread_mails',
        name='unread/mails'),
    url(r'^mail/reply$', 'mail_reply', name="mail/reply"),
    url(r'^mail/validate$', 'mail_validate', name="mail/validate"),
    url(r'^createLabel/$', 'createLabel', name="mail/createLabel"),
    url(r'^label-list/$', 'label_list', name='mail/label_list'),
    url(r'^add-label/$', 'add_label', name='mail/add_label'),
    url(r'^delete-label/$', 'delete_label', name='mail/delete_label'),
    url(r'^move-thread/$', 'move_thread', name='mail/move_thread'),
    url(r'^mail/contact/add$', 'add_contact', name='mail/contact/add'),
    url(r'^contact/list$', 'contact_list', name='mail/contact/list'),
    url(r'^view/addressbook$', 'addressbook_view' , name='view/address_book'),
    url(r'^edit/addressbook$', 'addressbook_edit' , name='edit/address_book'),

)
