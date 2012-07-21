# -*- coding: utf-8 -*-
from django.db                             import models




class Locatable(models.Model):
    u""" هر چیزی که به صورت یک نقطه روی نقشه قابل نمایش باشد.
    """
    
    glatlng             = models.CharField(u'موقعیت روی نقشه', max_length = 50, null = True, blank=True)
    boundary            = models.CharField(u'محدوده', max_length = 255, null = True, blank=True)
    prefered_zoom       = models.IntegerField(null = True, blank=True) #TODO: because of many null values, put this field in another supplementary table
    
    class Meta:
        abstract        = True


    def get_map_info(self):
        return {'title': unicode(self), 'description': self.description}
    
    def get_position(self):
        return self.glatlng

    def lat(self):
        if not self.glatlng:
            return 0
        return float(self.glatlng.split(',')[0])

    def lng(self):
        if not self.glatlng:
            return 0
        return float(self.glatlng.split(',')[1])

    def push_data_to(self, dic):
        dic.update({'lat': self.lat(), 'lng': self.lng(),
                   'zoom': self.prefered_zoom, 'boundary': self.boundary})
        return dic


class AbstractState(models.Model):
    name                = models.CharField(max_length = 50,blank=False)


    class Meta:
        abstract        = True

        verbose_name    = u"استان"
        verbose_name_plural = u"استان ها"


    def __unicode__(self):
        return self.name


class Place(models.Model):
    name                = models.CharField(u'نام', max_length = 50)
    address             = models.CharField(u'آدرس', max_length = 255, blank = True)


    class Meta:
        abstract        = True


    def __unicode__(self):
        return self.name