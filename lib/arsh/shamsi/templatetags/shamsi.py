# -*- coding:utf-8 -*-
from django                                import template

from arsh.shamsi.date.shamsi_date          import format_relative_date




__docformat__ = 'reStructuredText'

register = template.Library()


@register.filter
def relative(date):
    return format_relative_date(date)
