# -*- coding: utf-8 -*-
from django import template

from arsh.user_mail.config_manager import ConfigManager


__docformat__ = 'reStructuredText'


register = template.Library()
cf = ConfigManager.prepare()


@register.filter
def get_title(value):
    if cf.get("system-state") == 'mails':
        return u"تاریخ ایجاد پیام "
    return u"تاریخ ایجاد درخواست"