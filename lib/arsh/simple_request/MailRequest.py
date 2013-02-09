# -*- coding: utf-8 -*-
import logging
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from arsh.mail.models import Mail, Label
from arsh.simple_request import mail_request
from arsh.simple_request.models import SimpleRequest


logger = logging.getLogger()


class SimpleMailRequest:
    RADIUS = 1000  # 1 Kilometers
    RADIUS_EXPANSION_LIMIT = 5

    def __init__(self, requester, type, object=None, request=None):
        """
            :type request: SimpleRequest
        """
        self._requester = requester
        self._type = type
        self._object = object
        if request:
            self._is_new = False
            self._request = request
            self._thread = request.discussion_thread
        else:
            self._is_new = True
            self._request = SimpleRequest(request_object=self._object, requester=self._requester, type=type)
            self._thread = None

    def get_responders(self):
        from rezgh.places.models import Shop
        from rezgh.accounts.AccountManager import AccountManager

        if isinstance(self._object, Shop) and self._object.glatlng:
            admins = AccountManager.get_administrators().exclude(profile__glatlng='')
            admins_distance = self.admins_distance(admins)
            responder = self.eligible_responder(admins_distance)
            return [responder]

        return AccountManager.get_administrators().order_by('?')[:1]

    def admins_distance(self, admins):
        from rezgh.utils.gis import LatLng

        admins_distance = []

        for admin in admins:
            try:
                profile = admin.profile
            except ObjectDoesNotExist:
                continue
            admins_location = LatLng.parse(str(profile.glatlng)) if profile.glatlng else None
            if not admins_location:
                continue
            admins_distance.append(
                [admin, admins_location.calculate_distance_to(LatLng.parse(str(self._object.glatlng)))])
        if not admins_distance:
            for admin in admins:
                admins_distance.append([admin, 0])
        return admins_distance

    def eligible_responder(self, distances):
        eligible_admins = []
        distances.sort(key=lambda x: x[1])

        radius_expansion = 1
        while not eligible_admins and radius_expansion != SimpleMailRequest.RADIUS_EXPANSION_LIMIT:
            for admin, distance in distances:
                if distance < SimpleMailRequest.RADIUS * radius_expansion:
                    eligible_admins.append(admin)
            radius_expansion += 1

        # The closest person, the else case is never gonna happen !
        if eligible_admins:
            return eligible_admins[0]
        return distances[0][0]

    def get_title(self):
        return u'%s %s از سوی %s' % (self._type, self._object._meta.verbose_name, self._requester.get_full_name())

    def get_labels(self):
        from rezgh.accounts.AccountManager import AccountManager

        labels = [self._type]
        if AccountManager.is_manager(self._requester):
            labels += [Label.INBOX_LABEL_NAME]
        return labels

    def get_content(self):
        content = u"""
                <b>نوع درخواست: </b> %s %s<br/>
                <b>جزییات درخواست:</b><br/><ul>
            """ % (self._type, self._object._meta.verbose_name)  # TODO: farsi, template, show all object's fields
        for field in self._object.get_controlled_fields():
            if isinstance(field, models.Field):
                name = field.verbose_name
                value = field.value_to_string(self._object)
                value = '' if (value is None or value == u'None') else field.rel.to.objects.get(pk=value)
                if isinstance(field, models.ManyToManyField):
                    if value and value != '[]':
                        value = value.replace('L', '')  # skip longs!
                        value = u'، '.join(
                            [unicode(field.rel.to.objects.get(pk=vid)) for vid in value[1:-1].split(',')])
                    else:
                        value = u''
            else:
                name = field['name']
                value = field['value']
            content += u'<li><b>%s:</b> %s</li>' % (name, value)
        content += u'</ul>'
        return content

    def send(self):
        content = self.get_content()

        self._request.description = content
        self._request.save()

        if self._is_new:
            #adding simple_request meta
            content += '%s:REQ:%d\n' % (mail_request.FOOTER_SLUG, self._request.pk)
            content += 'accept,%s\nreject,%s\ntalk' % (self._request.url_accept, self._request.url_reject)

            responders = self.get_responders()
            logger.debug('request responders set to: ' + ', '.join(['user#%d' % r.id for r in responders]))
            if not responders:
                logger.warn('can not find any responders for request#%d' % self._request.id)
            mail = Mail.create(content, subject=self.get_title(), sender=self._requester, receivers=responders[:1],
                               cc=responders[1:], titles=self.get_labels(),
                               initial_sender_labels=[Label.SENT_LABEL_NAME] + self.get_labels(), thread=self._thread)
            self._request.discussion_thread = mail.thread
            self._request.save()
        else:
            Mail.reply(content, self._requester, thread=self._request.discussion_thread)


    @staticmethod
    def create(requester, type, object=None, continue_thread=True):
        """
        :type requester: User
        :type type: unicode
        """
        req = None
        if continue_thread:
            try:
                ct = ContentType.objects.get_by_natural_key(object._meta.app_label, object._meta.module_name)
                req = SimpleRequest.objects.get(requester=requester, request_object_id=object.id,
                                                object_content_type=ct, type=type)
            except SimpleRequest.DoesNotExist:
                pass
        return SimpleMailRequest(requester, type, object=object, request=req)
