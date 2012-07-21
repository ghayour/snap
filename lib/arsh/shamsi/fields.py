#encoding:UTF-8
import datetime
from string import split

from django.core import validators
from django.core.exceptions import ValidationError
from django import forms

from arsh.shamsi.widgets.shamsi_widget import ShamsiWidget, ShamsiAdminSplitDateTimeWidget
from arsh.shamsi.date.shamsi_date import pdate_separate_to_miladi

class ShamsiDateField(forms.DateField):
    widget = ShamsiWidget
    default_error_messages = {'invalid':u"یک تاریخ معتبر وارد نمایید."}

    #    def __init__(self, input_formats=None, *args, **kwargs):
    #        super(ShamsiDateField,self).__init__(input_formats=None, *args, **kwargs)
    #        if kwargs.has_key('initial'):
    #            new_initial = pdate_string(kwargs.get('initial'))
    #            kwargs.update({'initial':new_initial})

    def to_python(self, value):
        """
        Validates that the input can be converted to a date. Returns a Python
        datetime.date object.
        """
        if value in validators.EMPTY_VALUES:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            l1 = split(value, "-")
            year = int(l1[0])
            month = int(l1[1])
            day = int(l1[2])
            return pdate_separate_to_miladi(year, month, day)
        except ValidationError:
            raise ValidationError(self.default_error_messages['invalid'])


class ShamsiAdminSplitDateTimeField(forms.MultiValueField):
    """
    a form field that its date is  ShamsiDateField and its time is
    TimeFieldand its widget is ShamsiAdminSplitDateTimeWidget.
    this field is suitable for admin
    """
    widget = ShamsiAdminSplitDateTimeWidget
    default_error_messages = {
        'invalid_date': (u'یک تاریخ معتبر وارد نمایید.'),
        'invalid_time': (u'یک زمان معتبر وارد نمایید.'),
        }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages
        localize = kwargs.get('localize', False)
        fields = (
            ShamsiDateField(error_messages={'invalid': errors['invalid_date']}, localize=localize),
            forms.TimeField(error_messages={'invalid': errors['invalid_time']}, localize=localize),
            )
        super(ShamsiAdminSplitDateTimeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if data_list[0] in validators.EMPTY_VALUES:
                raise ValidationError(self.error_messages['invalid_date'])
            if data_list[1] in validators.EMPTY_VALUES:
                raise ValidationError(self.error_messages['invalid_time'])
            return datetime.datetime.combine(*data_list)
        return None

