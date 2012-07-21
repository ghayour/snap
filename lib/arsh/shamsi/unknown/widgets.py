# -*- coding: utf-8 -*-
from arsh.shamsi.date.calverter import  PersianDate
import datetime
import re

from django.forms.widgets import Widget, Select
from django.utils.safestring import mark_safe
from django.utils.formats import get_format

__all__ = ('PersianDateSelectWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

class PersianDateSelectWidget(Widget):
    none_value = (0, '---')
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            self.years = range(1389, 1401)

    def render(self, name, value, attrs=None):
        try:
            p = PersianDate(date=datetime.date(value.year, value.month, value.day))
            year_val, month_val, day_val = p.year, p.month, p.day
            if value is None:
                year_val = month_val = day_val = None
        except AttributeError:
            year_val = month_val = day_val = None

        MONTHS = [
            ('1', u"فروردین"),
            ('2', u"اردیبهشت"),
            ('3', u"خرداد"),
            ('4', u"تیر"),
            ('5', u"مرداد"),
            ('6', u"شهریور"),
            ('7', u"مهر"),
            ('8', u"آبان"),
            ('9', u"آذر"),
            ('10', u"دی"),
            ('11', u"بهمن"),
            ('12', u"اسفند"),
        ]

        choices = [(i, i) for i in self.years]
        year_html = self.create_select(name, self.year_field, value, year_val, choices)
        month_html = self.create_select(name, self.month_field, value, month_val, MONTHS)
        choices = [(i, i) for i in range(1, 32)]
        day_html = self.create_select(name, self.day_field, value, day_val, choices)

        format = get_format('DATE_FORMAT')
        escaped = False
        output = []
        for char in format:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char in 'Yy':
                output.append(year_html)
            elif char in 'bFMmNn':
                output.append(month_html)
            elif char in 'dj':
            # output.append(day_html)
                pass
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_

    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)

        if y == m == d == "0":
            return None
        p = PersianDate(year=int(y), month=int(m), day=1)
        if y == '0' or m == '0':
            return None
        greg = p.get_greg_date()
        y = greg.year
        m = greg.month
        d = greg.day

        if y and m and d:
            return '%s-%s-%s' % (y, m, d)

        return data.get(name, None)

    def create_select(self, name, field, value, val, choices):
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        if not (self.required and val):
            choices.insert(0, self.none_value)
        local_attrs = self.build_attrs(id=field % id_)
        s = Select(choices=choices)
        select_html = s.render(field % name, val, local_attrs)
        return select_html

  
