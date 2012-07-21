#encoding:UTF-8
import datetime

from django.utils.safestring import mark_safe
from django import forms
from django.contrib.admin.widgets import AdminTimeWidget
from arsh.shamsi.date.shamsi_date import pdate_separated


class ShamsiWidget(forms.DateInput):
    def render(self, name, value, attrs=None):
        input = super(ShamsiWidget, self).render(name, self.get_persian_value(value), attrs)
        output = '<div class="dateinput">' + input + '</div>'
        return mark_safe(output)

    def get_persian_value(self, value):
        if isinstance(value, datetime.datetime):
            date = value.date()
        elif isinstance(value, datetime.date):
            date = value
        else:
            return value
        year, month, day = pdate_separated(date)
        output = "-".join((str(year), str(month), str(day)))
        return output
		

class ShamsiAdminSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    یک ویجت است که تاریخ آن شمسی است و زمان آن به سبک زمان در قسمت ادمین است
    """

    def __init__(self, attrs=None):
        widgets = [ShamsiWidget, AdminTimeWidget]
        forms.MultiWidget.__init__(self, widgets, attrs)



