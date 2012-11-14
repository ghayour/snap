# -*- coding: utf-8 -*-
import uuid
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from arsh.mail.models import Thread
from arsh.db_models.common import Logged




class Controlled(models.Model):

    accepted            = models.NullBooleanField(null = True)


    class Meta:
        abstract = True


    def accept(self):
        self.accepted = True
        self.save()

    def reject(self):
        self.accepted = False
        self.save()

    def get_status_name(self):
        status = u''
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
    request_object_id   = models.PositiveIntegerField()
    request_object      = generic.GenericForeignKey('object_content_type', 'request_object_id')

    type                = models.CharField(max_length=255, default='')
    requester           = models.ForeignKey(User, null=True, blank=True)
    description         = models.TextField(null=True, blank=True)
    url_accept          = models.CharField(max_length=255, blank=True)
    url_reject          = models.CharField(max_length=255, blank=True)
    discussion_thread   = models.ForeignKey(Thread, null=True)


    def get_status(self):
        #noinspection PyUnresolvedReferences
        return self.request_object.accepted


    def get_edit_url(self):
        from rezgh.accounts.models import Profile
        from rezgh.places.models import Place
        obj = self.request_object
        if isinstance(obj, Profile):
            return reverse('show_profile')
        if isinstance(obj, Place):
            return '%s?action=edit_shop&id=%s' % (reverse('jobs/tree'), obj.id)
        return False


    def get_inspect_urls(self):
        from rezgh.accounts.models import Profile
        from rezgh.places.models import Place
        obj = self.request_object
        if isinstance(obj, Profile):
            return [(u'مشاهده پروفایل', reverse('show_profile')+'?user=%d'%self.requester_id)]
        if isinstance(obj, Place):
            return [(u'ارزیابی مغازه', '%s?action=edit_shop&id=%s' % (reverse('jobs/tree'), obj.id))]
        return []


    def save(self, *args, **kwargs):
        if self.id is None:
            prefix = reverse('simple_request/eval', kwargs={'url': 'a'})[:-1]
            self.url_accept = prefix + str(uuid.uuid4())
            self.url_reject = prefix + str(uuid.uuid4())
        super(SimpleRequest, self).save(*args, **kwargs)
