# -*- coding: utf-8 -*-

import factory
import random
import string

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client

from arsh.user_mail.models import Mail, Label, Thread

def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))

class ThreadFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Thread

    title=factory.LazyAttribute(lambda t: random_string())

class MailFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Mail

    title = factory.LazyAttribute(lambda t: random_string())
    content = factory.LazyAttribute(lambda t: random_string())
    thread=ThreadFactory.create()
    #recipients = None

class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.LazyAttribute(lambda t: random_string())
    first_name = factory.LazyAttribute(lambda t: random_string())
    last_name = factory.LazyAttribute(lambda t: random_string())
    password = factory.LazyAttribute(lambda t: random_string())


class MailTest(TestCase):
    fixtures = ['auth']

    def testMail(self):
        """
        دو کاربر و یک میل ایجاد می شود و سپس تست می شود و سپس یک میل از کاربر اول به کاربر دوم ارسال می شود.
        نهایتا چک می شود که آیا محتوای mail و label و thread خالی نباشد.
        """
        user1 = UserFactory.create()
        user2 = UserFactory.create()
        mail = MailFactory.create(content=u'This is test', sender=user1)#, subject=u'Test subject', receivers=None)
        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()
        mail.reply(content="hi", sender=user2, thread=mail.thread)  # Lines related to simple request is deleted
        thread = mail.thread
        label = Label.get_user_labels(user2)
        label2 = Label.get_user_labels(user1)
        # Assertions:
        self.assertIsNotNone(mail.recipients)
        self.assertIsNotNone(mail.content)
        self.assertIsNotNone(mail.thread)
        self.assertIsNotNone(mail.title)
        self.assertIsNotNone(mail.created_at)
        self.assertIsNotNone(label[0].INBOX_LABEL_NAME)
        self.assertIsNotNone(label[0].title)
        self.assertIsNotNone(label[0].user)
        self.assertIsNotNone(thread.labels)
        thread.remove_label(label[0])
        thread.remove_label(label2[0])

#
#class AppTest(TestCase):
#    fixtures = ['auth']
#
#    def setUp(self):
#        self.client = Client()
#        self.assertTrue(self.client.login(username='admin', password='admin'))
#
#    def testAdmin(self):
#        response = self.client.get('/admin/')
#        self.assertEqual(response.status_code, 200)
#
#    def testView(self):
#        response = self.client.get('/mail/view/')
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'mail/label.html')
#        self.assertTemplateUsed(response, 'mail/mail_template.html')
#        self.assertTemplateUsed(response, 'base.html')
#
#    def testCompose(self):
#        response = self.client.get('/mail/compose')
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'mail/composeEmail.html')
#        self.assertEqual(Mail.objects.all().exists(), False)
#        self.client.post('/mail/compose',
#                         data={'recipients': 'admin', 'title': 'test_title', 'cc': '', 'bcc': '',
#                               'content': '<p>test_contents</p>'})
#        self.assertEqual(Mail.objects.all().exists(), True)
#        self.assertEqual(Thread.objects.all().exists(), True)
#
#    def testArchive(self):
#        response = self.client.get('/mail/view/archive/')
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'mail/label.html')
#
#    def testSetUp(self):
#        response = self.client.get('/mail/setup')
#        self.assertEqual(response.status_code, 200)
