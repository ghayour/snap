#coding=utf-8
__docformat__ = 'reStructuredText'

import datetime
from django.template import Library
from arsh.shamsi.date.shamsi_date import get_jalali, pdate_persian_month_weekday, pdate_persian_month

MONTHS = (
    "فروردين", "ارديبهشت", "خرداد", "تير", "مرداد", "شهريور", "مهر", "آبان", "آذر", "دي", "بهمن", "اسفند")

register = Library()

@register.filter
def pdate(value):
    """
    example : 1 تير 1391

    :type value:datetime.date
    """
    return pdate_persian_month(value)

@register.filter
def pdatetime(value):
    """
    show persian date and time.
    example: 1 تير 1391 17:41:45
    :type value: datetime.datetime
    """
    jalali = get_jalali(value)
    return str(jalali[2]) + " " + MONTHS[jalali[1] - 1] + " " + str(jalali[0]) + " " + "%d:%d:%d" % (
        value.hour, value.minute, value.second)

@register.filter
def pdate_weekday(value):
    """
    example: پنجشنبه 1 تير 1391

    :type value:datetime.date
    """
    return pdate_persian_month_weekday(value)

@register.simple_tag
def pdate_weekday_today():
    """
    represent today persian datetime.
    example: پنجشنبه 1 تير 1391
    """
    return pdate_persian_month_weekday(datetime.datetime.now())
