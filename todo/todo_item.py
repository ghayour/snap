# -*- coding: utf-8 -*-
import re
from datetime import date, timedelta
from django.conf import settings
from arsh.shamsi.date.shamsi_date import Shamsi
from arsh.user_mail.models import Label


class TodoItem(object):
    def __init__(self, thread=None, title=None, start=None, due=None,
                 assigner=None, assignee=None, watchers=None):
        u"""
            :param arsh.user_mail.models.Thread thread: ترد مربوطه
            :param date start: تاریخ شروع کار
            :param date due: تاریخ مهلت انجام کار
            :param User assigner: کسی که این کار را محول کرده است
            :param list of User assignee: لیستی از افرادی که کار به آن ها واگذار شده
            :param list of User assignee: لیستی از افراد ناظر انجام کار
        """
        self.thread = thread
        self.start = start
        self.due = due
        self.title = title
        self.assigner = assigner
        self.assignee = list(assignee)
        self.watchers = list(watchers)

    def is_personal(self):
        u""" آیا این یک کار شخصی است؟ کار شخصی کاری است که یک فرد برای خودش تعیین می کند

            :rtype: bool
        """
        return self.assignee == [self.assigner] and not self.watchers

    def sync(self):
        try:
            calendar_system = settings.INTEGRATED_SYSTEMS['arsh_calendar']
        except (AttributeError, KeyError):
            return False

        todo = {
            'title': self.title,
            'start_date': Shamsi(self.start).strfshamsi(Shamsi.SHORT_DATE),
            'due_date': Shamsi(self.due).strfshamsi(Shamsi.SHORT_DATE),
            'priority': 2,
            'status': 1,
            'creator_username': self.assigner.username,
            'assignee_username': self.assignee[0].username,
        }

        import requests
        r = requests.post(calendar_system['url'] + 'calendar/create_todo_please/', data=todo)
        if r.status_code != 200:
            raise ValueError("[Error] Unexpected status code: {0}".format(r.status_code))
        return True

    @classmethod
    def try_parse_thread(cls, thread, user=None, check_todo_label=True):
        """

            :param arsh.user_mail.models.Thread thread: mail to be parsed
            :rtype: TodoItem or None
        """
        UNIT_CONVERSION = {
            u'روز': lambda d: d,
            u'هفته': lambda d: d * 7,
            u'ماه': lambda d: d * 30,    # TODO: or 31?
            u'سال': lambda d: d * 365,   # TODO: or 366?
        }

        if check_todo_label:
            if not thread.has_label(Label.get_label_for_user(Label.STD_LABELS['todo'], user)):
                return None

        mail = thread.first_mail
        m = re.search(re.compile(ur'مهلت\s+انجام\s*(?::)?\s*(?P<len>\d+)\s*(?P<unit>روز|هفته|ماه|سال)', re.UNICODE),
                      mail.content)
        if not m:
            return None

        days = int(m.group('len'))
        try:
            days = UNIT_CONVERSION[m.group('unit')](days)
        except KeyError:
            assert False, 're unit choices must be defined in UNIT_CONVERSION array'
        sd = mail.created_at.date()
        dd = sd + timedelta(days=int(days))
        rep = mail.get_recipients()
        assignee = [r.user for r in rep['to']]
        watchers = [r.user for r in rep['cc']]
        item = TodoItem(thread=thread, start=sd, due=dd, title=thread.title, assigner=mail.sender,
                        assignee=assignee, watchers=watchers)
        return item

    @classmethod
    def get_candidate_threads(cls, user):
        return Label.get_label_threads(user, Label.STD_LABELS['todo'])

    @classmethod
    def get_all_user_todos(cls, user):
        todos = []
        for t in cls.get_candidate_threads(user):
            item = cls.try_parse_thread(t, check_todo_label=False)
            if item:
                todos.append(item)
        return todos
