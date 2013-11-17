# -*- coding:utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter

from arsh.shamsi.date.shamsi_date import pdate_time_persian_month, pdate, pdate_persian_month

__docformat__ = 'reStructuredText'

register = template.Library()

@register.filter()
def shamsi(value):
    """
این فیلتر تاریخ استفاده شده در قالب را به شمسی تبدیل می کند
    :param value:
    :return:
    """
    return pdate_time_persian_month(value)


@register.filter()
def shamsi_date(value):
    """
این فیلتر تاریخ استفاده شده در قالب را به شمسی تبدیل می کند
    :param value:
    :return:
    """
    return pdate_persian_month(value)