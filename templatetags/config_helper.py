# -*- coding: utf-8 -*-
from django import template

from arsh.user_mail.config_manager import ConfigManager


register = template.Library()


@register.filter
def get_configured_title(value):
    cf = ConfigManager.prepare()
    if value == 'thread-date':
        if cf.get("system-state") == 'mails':
            return u"تاریخ ایجاد پیام "
        return u"تاریخ ایجاد درخواست"
    return value
