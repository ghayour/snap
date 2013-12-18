# -*- coding: utf-8 -*-

import factory
import random
import string

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client

from arsh.user_mail.models import Mail, Label, Thread, MailDomain, MailAccount, MailProvider, DatabaseMailAccount
from arsh.user_mail.models import ReadMail


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


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

class DatabaseMailAccountFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DatabaseMailAccount

class TestModelFunc(TestCase):
    fixtures = ['auth']

    def test_send_mail(self):
        #TODO: 1: ask how should I set reciever adress? its getting no such user error
        user1 = UserFactory.create(username='sender',email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciver',email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        user1_account=DatabaseMailAccountFactory.create(user=user1,provider=mail_provider ,email=user1.email)
        user2_account=DatabaseMailAccountFactory.create(user=user2,provider=mail_provider ,email=user2.email)

        mail = MailFactory.create(content=u'This is send mail test', sender=user1)
        #, subject=u'Test subject', receivers=None)
        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()
        thread = mail.thread
        label2 = Label.get_user_labels(user2)
        label1 = Label.get_user_labels(user1)
        # Assertions:
        self.assertIsNotNone(mail.recipients)
        self.assertIsNotNone(mail.content)
        self.assertIsNotNone(mail.thread)
        self.assertIsNotNone(mail.title)
        self.assertIsNotNone(mail.created_at)
        #TODO: 2: ask how to check the target has recieved the mail?
        #TODO: 3: ask where is SENT_LABEL?
        print label1
        print label2
        #Check INBOX and SENT labels
        self.assertIsNotNone(label1[0])
        self.assertIsNotNone(label2[0])
        self.assertIsNotNone(label1[0].SENT_LABEL_NAME)
        self.assertIsNotNone(label2[0].INBOX_LABEL_NAME)
        self.assertIsNotNone(label1[0].title)
        self.assertIsNotNone(label2[0].title)

        self.assertIsNotNone(thread.labels)





    def test_reply_mail(self):
        """
        دو کاربر و یک میل ایجاد می شود و سپس تست می شود و سپس یک میل از کاربر اول به کاربر دوم ارسال می شود.
        نهایتا چک می شود که آیا محتوای mail و label و thread خالی نباشد.
        """
        user1 = UserFactory.create(username='sender',email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciver',email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        user1_account=DatabaseMailAccountFactory.create(user=user1,provider=mail_provider ,email=user1.email)
        user2_account=DatabaseMailAccountFactory.create(user=user2,provider=mail_provider ,email=user2.email)

        mail = MailFactory.create(content=u'This is reply test', sender=user1)
        #, subject=u'Test subject', receivers=None)
        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()

        #TODO: 4: ask: reply recievers should'nt be add in reply method
        #TODO: They should be suggested in form and editable for the user

        #TODO: in this manner user1 should NOT recieve reply
        mail.reply(content="hi", sender=user2, thread=mail.thread)

        thread = mail.thread
        label1 = Label.get_user_labels(user1)
        label2 = Label.get_user_labels(user2)
        # Assertions:
        self.assertIsNone(mail.recipients)
        self.assertIsNotNone(mail.content)
        self.assertIsNotNone(mail.thread)
        self.assertIsNotNone(mail.title)
        self.assertIsNotNone(mail.created_at)
        self.assertIsNotNone(label1[0].INBOX_LABEL_NAME)
        self.assertIsNotNone(label1[0].title)
        self.assertIsNotNone(label1[0].user)
        self.assertIsNotNone(thread.labels)

        #TODO: ask: here user1 recieves the email
        mail.reply(content="hi", sender=user2, thread=mail.thread,receivers=user1)
        thread = mail.thread
        label1 = Label.get_user_labels(user1)
        label2 = Label.get_user_labels(user2)
        # Assertions:
        self.assertIsNotNone(mail.recipients)
        self.assertIsNotNone(mail.content)
        self.assertIsNotNone(mail.thread)
        self.assertIsNotNone(mail.title)
        self.assertIsNotNone(mail.created_at)
        self.assertIsNotNone(label1[0].INBOX_LABEL_NAME)
        self.assertIsNotNone(label1[0].title)
        self.assertIsNotNone(label1[0].user)
        self.assertIsNotNone(thread.labels)




    def test_add_label(self):
        user1 = UserFactory.create(username='sender',email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciver',email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        user1_account=DatabaseMailAccountFactory.create(user=user1,provider=mail_provider ,email=user1.email)
        user2_account=DatabaseMailAccountFactory.create(user=user2,provider=mail_provider ,email=user2.email)

        mail = MailFactory.create(content=u'This is test add label', sender=user1)
        #, subject=u'Test subject', receivers=None)

        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()
        user2_label=LabelFactory.create(user=user2, title="test lable user2",account=user2_account)
        user1_label=LabelFactory.create(user=user2, title="test lable user1",account=user1_account)
        mail.add_label(user1_label)
        mail.add_label(user2_label)
        thread = mail.thread
        label1 = Label.get_user_labels(user1)
        label2 = Label.get_user_labels(user2)
        # Assertions:
        self.assertIsNotNone(mail.recipients)
        self.assertIsNotNone(mail.content)
        self.assertIsNotNone(mail.thread)
        self.assertIsNotNone(mail.title)
        self.assertIsNotNone(mail.created_at)
        self.assertIsNotNone(label1[0].INBOX_LABEL_NAME)
        self.assertIsNotNone(label1[0].title)
        self.assertIsNotNone(label1[0].user)
        self.assertIsNotNone(thread.labels)
        #TODO: 5: ask how to check labels are added correct
        self.assertContains(user1_label,label1)
        self.assertContains(user2_label,label2)
        self.assertNotContains(user1_label,label2)
        self.assertNotContains(user2_label,label1)

    def test_mark_as_read_unread(self):
        user1 = UserFactory.create(username='sender',email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciver',email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        user1_account=DatabaseMailAccountFactory.create(user=user1,provider=mail_provider ,email=user1.email)
        user2_account=DatabaseMailAccountFactory.create(user=user2,provider=mail_provider ,email=user2.email)

        mail = MailFactory.create(content=u'This is test add label', sender=user1)
        #, subject=u'Test subject', receivers=None)

        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()
        # 6:  mark as read should be true for user1 and false for user2
        self.assertTrue(ReadMail.has_read(user1,mail))
        self.assertFalse(ReadMail.has_read(user2,mail))

        ReadMail.mark_as_read(user2,[mail])
        ReadMail.mark_as_unread(user1,[mail])

        self.assertTrue(ReadMail.has_read(user2,mail))
        self.assertFalse(ReadMail.has_read(user1,mail))



    def test_remove_label(self):
        pass

    def test_send_attachment(self):
        pass

    def test_add_conract(self):
        pass

    def test_remove_contact(self):
        pass





#class TestUrl(TestCase):
#    fixtures = ['auth']
#
#    def setUp(self):
#        self.client = Client()
#        self.assertTrue(self.client.login(username='admin', password='admin'))
#
#    def test_admin(self):
#        response = self.client.get('/admin/')
#        self.assertEqual(response.status_code, 200)
#
#    def test_view(self):
#        response = self.client.get('/mail/view/')
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'mail/label.html')
#        self.assertTemplateUsed(response, 'mail/mail_template.html')
#        self.assertTemplateUsed(response, 'base.html')
#
#    def test_compose(self):
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
#    def test_archive(self):
#        response = self.client.get('/mail/view/archive/')
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'mail/label.html')
#
#    def test_set_up(self):
#        response = self.client.get('/mail/setup')
#        self.assertEqual(response.status_code, 200)
#

class MailTestViews(TestCase):
    pass