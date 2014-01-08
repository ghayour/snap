# -*- coding: utf-8 -*-
__author__ = 'Farzaneh'
import factory
import random
import string

from django.contrib.auth.models import User

from arsh.user_mail.models import Mail, Label, Thread, MailDomain, MailProvider, DatabaseMailAccount
from arsh.user_mail.models import ReadMail, Contact, AddressBook, Attachment, MailReply


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))
#similar in common


class MailDomainFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MailDomain
    name = factory.LazyAttribute(lambda t: random_string())


class MailProviderFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MailProvider

    #domains =MailDomainFactory.create(name='arshmail.ir')


class ThreadFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Thread

    title = factory.LazyAttribute(lambda t: random_string())


class MailFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Mail

    title = factory.LazyAttribute(lambda t: random_string())
    content = factory.LazyAttribute(lambda t: random_string())
    thread = ThreadFactory.create()
    #recipients = None


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.LazyAttribute(lambda t: random_string())
    first_name = factory.LazyAttribute(lambda t: random_string())
    last_name = factory.LazyAttribute(lambda t: random_string())
    password = factory.LazyAttribute(lambda t: random_string())


class LabelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Label


    #account = factory.LazyAttribute(lambda t: random_string())
    #user = factory.LazyAttribute(lambda t: random_string())
    #title = factory.LazyAttribute(lambda t: random_string())
    #


class ContactFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Contact


class MailReplyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MailReply


class AddressBookFactory(factory.DjangoModelFactory):
    FACTORY_FOR = AddressBook


class AttachmentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Attachment

    attachment = factory.django.FileField(filename='flower.jpg')


class DatabaseMailAccountFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DatabaseMailAccount
