# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import datetime

__docformat__ = 'reStructuredText'

class notificationType(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Notification(models.Model):
    name = models.CharField("عنوان", max_length=20)
    description = models.TextField("توضیحات")
    user = models.ForeignKey(User, verbose_name="کاربر")
    level_choices = (('W', 'Warning'),
                    ('I', 'Info'),
                    ('E', 'Error'))
    level = models.CharField("درجه اهمیت", max_length=7, choices = level_choices)
    created_at = models.DateTimeField("تاریخ ایجاد")
    type = models.ForeignKey(notificationType, verbose_name="نوع پیام")
    can_close = models.BooleanField("امکان حذف", blank=True)
    display_until = models.DateTimeField("تاریخ اعتبار", blank=True, null=True)
    display_count = models.PositiveIntegerField("تعداد دفعات نمایش", blank=True, null=True)

    def __unicode__(self):
        return self.name

    def return_display_count(self):
        if self.display_count:
            return self.display_count
        else:
            return None

    def can_display(self):
        currentTime = datetime.datetime.now()
        if self.display_count and self.display_until > currentTime:
            if self.display_count:
                self.display_count -= 1
                return True
            else:
                return False
        elif self.display_until > currentTime:
            return True
        else:
            return False



