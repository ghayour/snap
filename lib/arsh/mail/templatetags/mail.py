# -*- coding:utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

from arsh.common.html.builder import Builder
from arsh.mail.UserManager import UserManager
from arsh.mail.models import Label


__docformat__ = 'reStructuredText'

register = template.Library()


@register.simple_tag
def mail_label(label):
    unread = label.get_unread_count()
    unread_str = ' (%d)' % unread if unread else ''
    url = reverse('mail/see_label', args=[label.slug])
    return "<a href='%s'>%s%s</a>" % (url, unicode(label), unread_str)


@register.simple_tag
def label_list(user):
    """
    1+|user.labels| Query

    :param user:
    :return:
    """
    unread_label = UserManager.get(user).get_unread_label()
    labels = Label.objects.raw("""
        SELECT l.id,l.title,l.slug,
          (SELECT COUNT(*) FROM mail_thread_labels tl
            WHERE
              tl.label_id=l.id
            AND
              (SELECT COUNT(*) FROM mail_thread_labels tl2
                 WHERE tl2.label_id=%d AND tl2.thread_id=tl.thread_id
              )>0
          ) AS unread_threads_count
        FROM mail_label l
        WHERE l.user_id=%d AND l.title <> 'unread'
        ORDER BY title
    """ % (unread_label.id, user.id))
    b = Builder()
    ls = []
    for label in labels:
        unread = label.unread_threads_count
        unread_str = ' (%d)' % unread if unread else ''
        url = reverse('mail/see_label', args=[label.slug])
        ls.append("<div class='sidebar-item'><a href='%s'>%s%s</a></div><div class='sidebar-item-seperator'>"
                  "<div class='sep-t'></div><div class='sep-b'></div></div>" % (url, unicode(label), unread_str))
    b.list(ls)
    return b.render()


@register.simple_tag
def is_unread(thread, user):
    if thread.is_unread(user):
        return '*'
    return ''
