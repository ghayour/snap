# -*- coding: utf-8 -*-
from exceptions import ValueError

from random import choice
from string import letters, digits
from django.utils.html import strip_tags




def generate_slug(len = 30):
    """
        یک رشته‌ی تصادفی برای استفاده به عنوان اسلاگ برمی‌گرداند.

        @param int len: طول خروجی مد نظر
    """
    return ''.join(choice(letters + digits) for x in range(len)) #@UnusedVariable


def get_summary(text, max_length, striptags=False):
    """ متن داده شده را خلاصه می‌کند

    :type text: unicode
    :param text: متنی که باید خلاصه شود
    :type max_length: int
    :param max_length: حداکثر طول خلاصه‌ی حاصل
    :rtype: unicode
    :return: متن خلاصه شده
    """
    if striptags:
        text = strip_tags(text)
    if not max_length:
        return text
    if max_length < 0:
        raise ValueError('max_length can not be negative')
    summary = u''
    for word in text.split(u' '):
        summary += u' ' + word
        if len(summary) > max_length: break
    if len(summary) < len(text):
        summary += u'...'
    return summary
