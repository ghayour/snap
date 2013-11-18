# -*- coding:utf-8 -*-
from django import template

from arsh.shamsi.templatetags.shamsi_template_tags import pdate

__docformat__ = 'reStructuredText'

register = template.Library()

@register.filter()
def shamsi(value):
    """
این فیلتر تاریخ استفاده شده در قالب را به شمسی تبدیل می کند
    :param value:
    :return:
    """
    return pdate(value)


@register.filter()
def shamsi_date(value):
    """
این فیلتر تاریخ استفاده شده در قالب را به شمسی تبدیل می کند
    :param value:
    :return:
    """
    return pdate(value)