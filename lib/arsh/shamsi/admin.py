#encoding:UTF-8
from django.contrib.admin.options import ModelAdmin
from django.db import models
from django.db.models.fields import DateTimeField, DateField

from arsh.shamsi.fields import ShamsiDateField, ShamsiAdminSplitDateTimeField
from arsh.shamsi.date.shamsi_date import pdate_time_persian_month, pdate_persian_month



class ShamsiModelAdmin(ModelAdmin):
    """
	اين کلاس، فيلدهاي
	DateField , DateTimeField
	را در قسمت
	Admin
	 به صورت تاريخ شمسي در مي آورد تا کاربر
	بتواند تاريخ را به صورت شمسي وارد نمايد و
	همچنين اين فيلدها را به صورت شمسي نمايش مي دهد.

    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(ShamsiModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if isinstance(db_field, models.DateTimeField):
            field = ShamsiAdminSplitDateTimeField()
            field.label = db_field.verbose_name
        elif isinstance(db_field, models.DateField):
            field = ShamsiDateField()
            field.label = db_field.verbose_name
        return field

    def __init__(self,*args,**kwargs):
        result = ()
        for i in range(len(self.list_display)):
            field = self.list_display[i]
            verbose_name = field
            type = 0
            for model_field in args[0]._meta.fields:
                if model_field.name == field:
                    verbose_name = model_field.verbose_name
                    if isinstance(model_field, DateField):
                        type = 1
                    if isinstance(model_field, DateTimeField):
                        type = 2
                    break
            if type == 1:
                exec 'def ' + field + '_shamsi (obj): return pdate_persian_month(obj.' + field + ') \n' + field +\
                     '_shamsi.short_description = u"' + verbose_name + '"\nself.' + field + '_shamsi = ' + field + '_shamsi'
            if type == 2:
                exec 'def ' + field + '_shamsi (obj): return pdate_time_persian_month(obj.' + field + ') \n' + field +\
                     '_shamsi.short_description = u"' + verbose_name + '"\nself.' + field + '_shamsi = ' + field + '_shamsi'
            if type:
                field += "_shamsi"
            result += (field, )
        self.list_display = result
        super(ShamsiModelAdmin,self).__init__(*args,**kwargs)

