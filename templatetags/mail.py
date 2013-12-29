# -*- coding:utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

from arsh.common.html.builder import Builder
from arsh.user_mail.UserManager import UserManager
from arsh.user_mail.models import Label


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

    ls = {}  # dict of account_name -> list of its labels
    total_unread_mails = 0
    for label in sorted(labels, key=Label.get_label_ordering_func()):
        unread = label.unread_threads_count
        unread_str = ''
        if unread and label.title != Label.SENT_LABEL_NAME:
            total_unread_mails += unread
            unread_str = ' <span class="badge">%d</span>' % unread
        url = reverse('mail/see_label', args=[label.slug])
        classes = []
        if label.title == current_label:
            classes.append('current')
        std_name = label.get_std_name()
        if std_name:
            if not std_name in ['request', 'todo']:
                classes.append('iconed')
                classes.append('icon-' + std_name)

        row = """<a class='%s' href='%s'>%s%s</a>""" % (' '.join(classes), url, unicode(label), unread_str)
        if not label.account_name in ls:
            ls[label.account_name] = []
        ls[label.account_name].append(row)

    __b = b = Builder()
    for account_name, cur_list in ls.iteritems():
        b.open_tag('div', class_name='box-menu active')

        b.open_tag('div', class_name='box-menu-head')
        __b.tag('span', str(account_name), class_name='box-menu-title')
        __b.tag('span', '', class_name='box-menu-expand')
        b.close_tag('div')

        b.open_tag('div', class_name='box-menu-body')
        __b.list(cur_list)
        b.close_tag('div')

        b.close_tag('div')
    return b.render()


@register.simple_tag
def is_unread(thread, user):
    if thread.is_unread(user):
        return '*'
    return ''
