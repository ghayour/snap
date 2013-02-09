# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _

from arsh.common.algorithm.strings import generate_slug


class Named(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('name'))

    class Meta:
        abstract = True


class Logged(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    updated_at = models.DateTimeField(auto_now_add=True, auto_now=True, verbose_name=_('updated_at'))


class Slugged(models.Model):
    slug = models.CharField(max_length=30, db_index=True, verbose_name=_('slug'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = generate_slug(length=30)
        models.Model.save(self, *args, **kwargs)


class ReferenceModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def reload_cache(cls):
        cls._ref_cache = cls.objects.all()

    @classmethod
    def by_pk(cls, pk):
        for obj in cls.all():
            if obj.pk == pk:
                return obj
        return None

    #noinspection PyUnresolvedReferences
    @classmethod
    def all(cls):
        try:
            return cls._ref_cache
        except AttributeError:
            cls.reload_cache()
            return cls._ref_cache
