# -*- coding: utf-8 -*-
from django.conf.urls                      import patterns, url




urlpatterns = patterns('arshlib__user_mail.sample.views',
    url(r'^1$', 'sample1', name='sample1'),
)
