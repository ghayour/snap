# -*- coding:utf-8 -*-
from django import template

from arsh.user_mail.UserManager import UserManager


__docformat__ = 'reStructuredText'

register = template.Library()


@register.filter
def get_user_full_name(user):
    """

        :param user:
        :return:
    """
    if user is None:
        return u'ناشناس'
    if not (isinstance(user, int) or isinstance(user, long)):
        user = user.user_id
    if user is None:
        return u'ناشناس'
    u = UserManager.get(None).get_user(user)
    return u.get_full_name() or u.username
