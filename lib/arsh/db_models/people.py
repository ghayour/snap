# -*- coding: utf-8 -*-
from django.db import models




class Person(models.Model):
    GENDER_CHOICES = (
        (u'M', u'مرد'),
        (u'F', u'زن'),
    )

    MARRIED_CHOICES = (
        (u'S', u'مجرد'),
        (u'M', u'متاهل'),
    )


    first_name     = models.CharField(u"نام", max_length = 255)
    last_name      = models.CharField(u"نام خانوادگی", max_length = 255)
    national_code  = models.CharField(u"کد ملی", max_length = 25)
    gender         = models.CharField(u"جنسیت", max_length = 2, choices = GENDER_CHOICES)
    married        = models.CharField(u"وضعیت تاهل", max_length = 2, choices = MARRIED_CHOICES)


    @property
    def name(self):
        return u"%s %s" % (self.first_name, self.last_name)


    def __unicode__(self):
        return self.name

    class Meta:
        abstract        = True
