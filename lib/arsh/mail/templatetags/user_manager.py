# -*- coding:utf-8 -*-
from django                                import template

from arsh.mail.UserManager                 import UserManager




__docformat__ = 'reStructuredText'

register = template.Library()


@register.filter
def get_user_full_name(obj):
    """

    :param user:
    :return:
    """
    if not (isinstance(obj, int) or isinstance(obj, long)):
        obj = obj.user_id
    return UserManager.get(None).get_user(obj).get_full_name()
