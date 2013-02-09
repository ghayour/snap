# -*- coding: utf-8 -*-
import uuid
from datetime import date

from model_utils import Choices
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import models
from django.db.models.loading import get_model, get_app
from django.utils.translation import ugettext_lazy as _

from arsh.common.db.basic import Logged
from arsh.mail.models import Thread


class Controlled(models.Model):
    accepted = models.NullBooleanField(null=True)

    class Meta:
        abstract = True

    def accept(self):
        self.accepted = True
        self.save()

    def reject(self):
        self.accepted = False
        self.save()

    def get_status_name(self):
        if self.accepted is None:
            status = u'بررسی نشده'
        elif self.accepted:
            status = u'تایید شده'
        else:
            status = u'رد شده'
        return status

    def get_controlled_field_names(self):
        return [field.name for field in self._meta.fields + self._meta.many_to_many]

    def get_controlled_fields(self):
        a = []
        for name in self.get_controlled_field_names():
            if isinstance(name, str):
                a.append(self._meta.get_field(name))
            else:
                a.append({'name': name['name'], 'value': getattr(self, name['method'])()})
        return a


class SimpleRequest(Logged):
    object_content_type = models.ForeignKey(ContentType)
    request_object_id = models.PositiveIntegerField()
    request_object = generic.GenericForeignKey('object_content_type', 'request_object_id')

    type = models.CharField(max_length=255, default='')
    requester = models.ForeignKey(User, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url_accept = models.CharField(max_length=255, blank=True)
    url_reject = models.CharField(max_length=255, blank=True)
    discussion_thread = models.ForeignKey(Thread, null=True)

    def get_status(self):
        #noinspection PyUnresolvedReferences
        return self.request_object.accepted

    def get_edit_url(self):
        # TODO: use hooks to implement
        return False

    def get_inspect_urls(self):
        # TODO: use hooks to implement
        return []

    def save(self, *args, **kwargs):
        if self.pk is None:
            prefix = reverse('simple_request/eval', kwargs={'url': 'a'})[:-1]
            self.url_accept = prefix + str(uuid.uuid4())
            self.url_reject = prefix + str(uuid.uuid4())
        super(SimpleRequest, self).save(*args, **kwargs)


class M_request(Logged):
    requester = models.ForeignKey(User, null=True, blank=True)
    url_action = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=255, default='')
    discussion_thread = models.ForeignKey(Thread, null=True)

    def __add_request_item(self, m_id, app, model, field, prev_val, new_val):
        tmp = RequestItem()
        tmp.application = app
        tmp.model = model
        tmp.m_id = m_id
        tmp.field = field
        tmp.request = self
        tmp.prev_val = prev_val
        tmp.new_val = new_val
        tmp.status = 'P'
        tmp.save()
        return tmp

    def add_request_for_object(self, original_object, modified_object):
        meta = original_object._meta
        m_id = original_object.id
        for f in meta.fields:
            pval = original_object._meta.get_value(f.name)
            nval = modified_object._meta.get_value(f.name)
            if pval != nval:
                self.__add_request_item(m_id=m_id, app=meta.app_label, model=meta.module_name(), prev_val=pval.name,
                                        new_val=nval, field=f.name)
                #TODO: make original_object and modified_object as a list of tuples

    def requests(self):
        return self.request_items.all()


class RequestItem(models.Model):
    STATUS = Choices(('P', 'pending', _('pending')), ('A', 'accepted', _('accepted')), ('R', 'rejected', _('rejected')))

    application = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    m_id = models.PositiveIntegerField()
    field = models.CharField(max_length=255)
    request = models.ForeignKey(M_request, related_name='request_items')
    prev_val = models.CharField(max_length=255, blank=True)
    new_val = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=1, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateField(blank=True)

    def accept(self):
        self.status = 'A'
        self.answered_at = date.today()
        self.save()

    def reject(self):
        self.status = 'R'
        app = get_app(self.application)
        model = get_model(app, self.model)
        instance = model.objects.get(id=self.m_id)
        setattr(instance, self.field, self.prev_val)
        self.answered_at = date.today()
        self.save()
