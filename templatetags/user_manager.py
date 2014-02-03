# -*- coding:utf-8 -*-
from django import template

from arsh.user_mail.UserManager import UserManager
from arsh.user_mail.models import AddressBook

from django.shortcuts import render_to_response, get_object_or_404

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

@register.filter
def get_thread_senders(thread, user):
    mail_counts = len(thread.get_user_mails(user))
    senders = thread.get_senders(user)['senders']
    s = ''
    for sender in senders.all():
        full_name = sender.get_full_name()
        #add_book = AddressBook.objects.get(user = user).get_all_contacts()
        #email = sender.email
        #x = add_book.get_object_or_404(email = email)
        if sender == user:
            s = s + u"من" + u'، '
        else:
            if full_name == '':
                s = s + sender.username + u'، '
            else:
                s = s + sender.get_full_name() + u', '

    
    return s[:-2] + ' (%d)' % mail_counts