# -*- coding: utf-8 -*-

import factory
import random
import string

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client

from arsh.user_mail.models import Mail, Label, Thread, MailDomain, MailProvider, DatabaseMailAccount
from arsh.user_mail.models import ReadMail, Contact, AddressBook, MailReply

from factories import UserFactory, MailProviderFactory, MailDomainFactory, MailFactory, ThreadFactory
from factories import LabelFactory, MailFactory, ContactFactory, AddressBookFactory, DatabaseMailAccountFactory
from factories import DatabaseMailAccountFactory


fixtures = ['test_admin_users']


class TestModelFunc(TestCase):

    def test_send_mail(self):
        #TODO: 1: again logic about email=username@default_provider is critical in sending emails
        user1 = UserFactory.create(username='sender',email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciever',email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        #user1_account = DatabaseMailAccountFactory.create(user=user1, provider=mail_provider, email=user1.email)
        #user2_account = DatabaseMailAccountFactory.create(user=user2, provider=mail_provider, email=user2.email)

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
        #TODO: 3: ask where is SENT_LABEL? done!
        print label1
        print label2
        #Check INBOX and SENT labels
        self.assertNotEqual(list(label1), [])
        self.assertNotEqual(list(label2), [])
        self.assertTrue(mail.has_label(LabelFactory.create(user=user1, title=Label.SENT_LABEL_NAME)))
        self.assertTrue(mail.has_label(LabelFactory.create(user=user2, title=Label.INBOX_LABEL_NAME)))
        self.assertIsNotNone(thread.labels)

    def test_reply_mail(self):
        """
        دو کاربر و یک میل ایجاد می شود و سپس تست می شود و سپس یک میل از کاربر اول به کاربر دوم ارسال می شود.
        نهایتا چک می شود که آیا محتوای mail و label و thread خالی نباشد.
        """
        user1 = UserFactory.create(username='sender', email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciever', email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        #user1_account = DatabaseMailAccountFactory.create(user=user1, provider=mail_provider, email=user1.email)
        #user2_account = DatabaseMailAccountFactory.create(user=user2, provider=mail_provider, email=user2.email)

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
        # Assertions:
        self.assertIsNone(mail.recipients)
        self.assertIsNotNone(mail.content)
        self.assertIsNotNone(mail.thread)
        self.assertIsNotNone(mail.title)
        self.assertIsNotNone(mail.created_at)
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
        self.assertIsNotNone(thread.labels)
        self.assertNotEqual(list(label1), [])
        self.assertNotEqual(list(label2), [])
        self.assertTrue(mail.has_label(LabelFactory.create(user=user1, title=Label.SENT_LABEL_NAME)))
        self.assertTrue(mail.has_label(LabelFactory.create(user=user2, title=Label.INBOX_LABEL_NAME)))
        self.assertIsNotNone(thread.labels)

    def test_add_label(self):
        user1 = UserFactory.create(username='sender', email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciever', email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        user1_account = DatabaseMailAccountFactory.create(user=user1, provider=mail_provider, email=user1.email)
        user2_account = DatabaseMailAccountFactory.create(user=user2, provider=mail_provider, email=user2.email)

        mail = MailFactory.create(content=u'This is test add label', sender=user1)
        #, subject=u'Test subject', receivers=None)

        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()
        user2_label = LabelFactory.create(user=user2, title="test lable user2", account=user2_account)
        user1_label = LabelFactory.create(user=user2, title="test lable user1", account=user1_account)
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
        self.assertIsNotNone(thread.labels)
        self.assertNotEqual(list(label1), [])
        self.assertNotEqual(list(label2), [])
        #TODO: 5: ask how to check labels are added correct
        self.assertTrue(mail.has_label(user2_label))
        self.assertTrue(mail.has_label(user1_label))

    #def test_forward(self):
    #    user1 = UserFactory.create()
    #    user2 = UserFactory.create()
    #    user3 = UserFactory.create()
    #    mail_provider = MailProviderFactory.create()
    #    mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
    #    mail = MailFactory.create(content=u'This is Forward test', sender=user1)
    #    #, subject=u'Test subject', receivers=None)
    #    # Testing functions:
    #    mail.add_receiver(mail, mail.thread, user2.email)
    #    mail.get_recipients()
    #    mail.get_summary()
    #    mail.(content="hi", sender=user2, thread=mail.thread)  # Lines related to simple request is deleted
    
    def test_mark_as_read_unread(self):
        user1 = UserFactory.create(username='sender', email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciever', email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        #user1_account = DatabaseMailAccountFactory.create(user=user1, provider=mail_provider, email=user1.email)
        #user2_account = DatabaseMailAccountFactory.create(user=user2, provider=mail_provider, email=user2.email)

        mail = MailFactory.create(content=u'This is test add label', sender=user1)
        #, subject=u'Test subject', receivers=None)

        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()
        # 6:  mark as read should be true for user1 and false for user2
        self.assertTrue(ReadMail.has_read(user1, mail))
        self.assertFalse(ReadMail.has_read(user2, mail))

        ReadMail.mark_as_read(user2, [mail])
        ReadMail.mark_as_unread(user1, [mail])

        self.assertTrue(ReadMail.has_read(user2, mail))
        self.assertFalse(ReadMail.has_read(user1, mail))

    #def test_remove_label(self):
    #    pass
    #
    def test_send_attachment(self):
        user1 = UserFactory.create(username='sender', email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciever', email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        #user1_account=DatabaseMailAccountFactory.create(user=user1, provider=mail_provider, email=user1.email)
        #user2_account=DatabaseMailAccountFactory.create(user=user2, provider=mail_provider, email=user2.email)

        mail = MailFactory.create(content=u'This is send mail test', sender=user1)

        # Testing functions:
        mail.add_receiver(mail, mail.thread, user2.email)
        mail.get_recipients()
        mail.get_summary()
        #thread = mail.thread
        #    label = Label.get_user_labels(user2)
        #    label2 = Label.get_user_labels(user1)
        #    # Assertions:
        #    self.assertIsNotNone(mail.recipients)
        #    self.assertIsNotNone(mail.content)
        #    self.assertIsNotNone(mail.thread)
        #    self.assertIsNotNone(mail.title)
        #    self.assertIsNotNone(mail.created_at)
        #    self.assertIsNotNone(label[0].INBOX_LABEL_NAME)
        #    self.assertIsNotNone(label[0].title)
        #    self.assertIsNotNone(label[0].user)
        #    self.assertIsNotNone(thread.labels)
        #    thread.remove_label(label[0])
        #    thread.remove_label(label2[0])

        label1 = Label.get_user_labels(user1)
        label2 = Label.get_user_labels(user2)
        self.assertFalse(mail.has_attachment())
        self.assertIsNotNone(label1)
        self.assertIsNotNone(label2)
        self.assertNotEqual(list(label1), [])
        self.assertNotEqual(list(label2), [])
        print "test attach"
        i = 1
        for a in label1:
            print i
            i += 1
            print a.title
            if a.title == Label.SENT_LABEL_NAME:
                print "True\n"
            else:
                print "Fals\n"

    def test_add_conract(self):
        user1 = UserFactory.create(username='sender', email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciever', email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        #user1_account = DatabaseMailAccountFactory.create(user=user1, provider=mail_provider ,email=user1.email)
        #user2_account = DatabaseMailAccountFactory.create(user=user2, provider=mail_provider ,email=user2.email)

        address_book1 = AddressBookFactory.create(user=user1)
        contact2 = ContactFactory.create(address_book=address_book1, email=user2.email)

        self.assertTrue(address_book1.has_contact(contact2))
        self.assertIsNotNone(address_book1.get_all_contacts())
        self.assertTrue(address_book1.has_contact_address(user2.email))
        self.assertIsNotNone(AddressBook.get_addressbook_for_user(user1))
        self.assertIsNone(AddressBook.get_addressbook_for_user(user2))
        self.assertFalse(address_book1.has_contact_address(user1.email))

    def test_remove_contact(self):
        user1 = UserFactory.create(username='sender', email="sender@arshmail.ir")
        user2 = UserFactory.create(username='reciever', email="reciever@arshmail.ir")
        mail_provider = MailProviderFactory.create()
        mail_provider.domains.add(MailDomainFactory.create(name='arshmail.ir'))
        #user1_account = DatabaseMailAccountFactory.create(user=user1, provider=mail_provider, email=user1.email)
        #user2_account = DatabaseMailAccountFactory.create(user=user2, provider=mail_provider, email=user2.email)

        self.assertIsNone(AddressBook.get_addressbook_for_user(user1))
        address_book1 = AddressBook.get_addressbook_for_user(user1, create_new=True)
        self.assertIsNotNone(AddressBook.get_addressbook_for_user(user1))
        self.assertEqual(list(address_book1.get_all_contacts()), [])
        #TODO: comment: the logic is how that the email should be exactly username@default_domain or we would get error
        #TODO: comment: so it seems we should not allow setting email address separately or fix the logic

        address_book1.add_contact_by_user(user2)
        #print "salam"
        #all=address_book1.get_all_contacts()
        #for a in all:
        #    print a.email
        #    print "\n"
        self.assertTrue(address_book1.has_contact_address(user2.email))

        address_book1.remove_contact_address(user2.email)
        self.assertFalse(address_book1.has_contact_address(user2.email))

    def test_mail_reply_thread(self):
        pass

    def test_mail_forward_thread(self):
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


class AppTest(TestCase):
    fixtures = ['test_admin_user', 'arshmail']

    def setUp(self):
        self.client = Client()
        self.assertTrue(self.client.login(username='test_admin_user', password='admin'), 'login failed')

    def test_admin(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_view(self):
        response = self.client.get('/view/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail/label.html')
        self.assertTemplateUsed(response, 'mail/mail_template.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_compose(self):
        response = self.client.get('/compose')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail/composeEmail.html')
        self.assertEqual(Mail.objects.all().exists(), False)
        self.client.post('/compose', data={
            'mail_uid': 'test_mail_uid_1',
            'receivers': 'test_admin_user@arshmail.ir',
            'cc': '',
            'bcc': '',
            'title': 'test_title',
            'content': '<p>test_contents</p>',
        })
        self.assertEqual(Mail.objects.all().exists(), True)
        self.assertEqual(Thread.objects.all().exists(), True)

    def test_archive(self):
        response = self.client.get('/view/archive/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail/label.html')

    def test_set_up(self):
        response = self.client.get('/setup')
        self.assertEqual(response.status_code, 200)
