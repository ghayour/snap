# -*- coding: utf-8 -*-
import random
import string

from django.db                             import models




class Logged(models.Model):

    class Meta:
        abstract = True


    created_at          = models.DateTimeField(auto_now_add = True)
    updated_at          = models.DateTimeField(auto_now_add = True, auto_now = True)



class Slugged(models.Model):
    slug                = models.CharField(max_length = 50, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        slug = ''
        if self.id is None:
            slug = ''.join(random.choice(string.letters + string.digits) for x in range(30))
            self.slug = slug
        models.Model.save(self, *args, **kwargs)
