# -*- coding:utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

from arsh.common.html.builder import Builder
from arsh.user_mail.UserManager import UserManager
from arsh.user_mail.models import Label, Thread


__docformat__ = 'reStructuredText'

register = template.Library()


@register.simple_tag
def mail_label(label):
    unread = label.get_unread_count()
    unread_str = ' (%d)' % unread if unread else ''
    url = reverse('mail/see_label', args=[label.slug])
    return "<a href='%s'>%s%s</a>" % (url, unicode(label), unread_str)


@register.simple_tag
def label_list(user, current_label=''):
    """
    1+|user.labels| Query

    :param user:
    :return:
    """
    total_unread_mails = 0
    unread_label = UserManager.get(user).get_unread_label()
    labels = Label.objects.raw("""
        SELECT l.id,l.title,l.slug,ma.email AS account_name,
          (SELECT COUNT(*) FROM user_mail_threadlabel tl
            WHERE
              tl.label_id=l.id
            AND
              (SELECT COUNT(*) FROM user_mail_threadlabel tl2
                 WHERE tl2.label_id=%d AND tl2.thread_id=tl.thread_id
              )>0
          ) AS unread_threads_count
        FROM user_mail_label l
        INNER JOIN user_mail_mailaccount ma
        ON (l.account_id = ma.id)
        WHERE l.user_id=%d AND l.title <> 'unread'
        ORDER BY title
    """ % (unread_label.id, user.id))
    b = Builder()
    ls = {}
    initial = Label.get_initial_labels()
    ordered_list = {}
    for label in labels:
        # unread = label.unread_threads_count
        unread = 0
        for t in label.threads.all():
            unread += len(t.get_unread_mails(user))
            if label.title != Label.SENT_LABEL_NAME:
                total_unread_mails += unread
        unread_str = ''
        if label.title != Label.SENT_LABEL_NAME:
            unread_str = ' <span class="badge">%d</span>' % unread if unread else ''
        url = reverse('mail/see_label', args=[label.slug])
        current_class = 'current' if label.title == current_label else ''

        if not label.account_name in ls:
            ls[label.account_name] = []

        row = """<div class='sidebar-item'><a class='%s' href='%s'>%s%s</a></div><div class='sidebar-item-seperator'>
        <div class='sep-t'></div><div class='sep-b'></div></div>""" % (current_class, url, unicode(label), unread_str)
        if label.title in initial:
            ordered_list[label.title] = (label.account_name, row)

        ls[label.account_name].append(row)
    for l in initial[::-1]:
        l = ordered_list.get(l, None)
        if l:
            ls[l[0]].remove(l[1])
            ls[l[0]].insert(0, l[1])

    for account_name, cur_list in ls.iteritems():
        b.tag('h6', str(account_name))
        b.list(cur_list)
        b.hr()
    return b.render()


@register.simple_tag
def is_unread(thread, user):
    if thread.is_unread(user):
        return '*'
    return ''

