# -*- coding: utf-8 -*-
import datetime
import logging

from model_utils import Choices
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, connection
from django.utils.translation import ugettext_lazy as _

from arsh.common.db.basic import Slugged, Named
from arsh.common.algorithm.strings import get_summary
from .Manager import DecoratorManager

__docformat__ = 'reStructuredText'

logger = logging.getLogger()

FOOTER_SLUG = 'sdhf3akj22sf5hljhuh243u423yr87fdyshd8c'


class MailDomain(Named):
    class Meta:
        verbose_name = u"دامنه میل"
        verbose_name_plural = u"دامنه‌های میل"

    def get_provider(self):
        #TODO: ask about this part logic
        try:
            return MailProvider.objects.get(domains=self)
        except MailProvider.DoesNotExist:
            return None


class MailProvider(Named):
    class Meta:
        verbose_name = u"ارائه دهنده میل"
        verbose_name_plural = u"ارائه دهندگان میل"

    domains = models.ManyToManyField(MailDomain, related_name='+')  # with implicit unique constraint

    @classmethod
    def get_default_domain(cls):
        return 'arshmail.ir'

    @classmethod
    def get_default_provider(cls):
        return cls.objects.get(domains__name=cls.get_default_domain())


class MailAccount(models.Model):
    class Meta:
        verbose_name = u"حساب کاربری میل"
        verbose_name_plural = u"حساب‌های کاربری میل"

    user = models.ForeignKey(User, related_name='mail_accounts')
    provider = models.ForeignKey(MailProvider, related_name='mail_accounts')
    email = models.CharField(max_length=100)

    def can_compose(self):
        raise NotImplementedError


class ProviderImapSettings(Named):
    class Meta:
        verbose_name = u"تنظیمات ارايه دهنده آی.مپ"
        verbose_name_plural = u"تنظیمات ارائه‌دهندگان آی.مپ"

    IMAP_SECURITY_TYPES = Choices(('N', 'none'), ('T', 'starttls'), ('S', 'ssl'))
    IMAP_AUTHENTICATION_METHOD = Choices(('p', 'password'), ('e', 'encrypted_password'), ('n', 'ntlm'),
                                         ('c', 'tls_certificate'), ('k', 'kerberos'))

    provider = models.ForeignKey(MailProvider, related_name='+')
    imap_server = models.CharField(max_length=100)
    imap_port = models.IntegerField()
    imap_security = models.CharField(max_length=1, choices=IMAP_SECURITY_TYPES)
    imap_authentication = models.CharField(max_length=1, choices=IMAP_AUTHENTICATION_METHOD)


class ImapMailAccount(MailAccount):
    class Meta:
        verbose_name = u"حساب کاربری آی.مپ"
        verbose_name_plural = u"حساب‌های کاربری آی.مپ"

    password = models.CharField(max_length=100)
    selected_imap_settings = models.ForeignKey(ProviderImapSettings)

    def can_compose(self):
        return False


class DatabaseMailAccount(MailAccount):
    class Meta:
        verbose_name = u"حساب کاربری محلی - پایگاه داده"
        verbose_name_plural = u"حساب‌های کاربری محلی - پایگاه داده"

    def can_compose(self):
        return True


class Mail(models.Model):
    sender = models.ForeignKey(User, related_name='sender', verbose_name=u'فرستنده')
    #TODO: ask: what if  reciever is out of this system!
    recipients = models.ManyToManyField(User, through='MailReceiver')
    title = models.CharField(max_length=300, verbose_name=u'عنوان')
    content = models.TextField(verbose_name=u'متن نامه')
    created_at = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey('Thread', related_name='mails')

    def __unicode__(self):
        return self.title

    def get_recipients(self):
        all_rec = self.mailreceiver_set.all()
        rec = {'to': [], 'cc': [], 'bcc': []}
        for r in all_rec:
            rec[r.type].append(r)
        return rec

    def get_summary(self):
        from HTMLParser import HTMLParser

        env = {'content': self.content}
        DecoratorManager.get().activate_hook('get_mail_summary', env, self)
        return get_summary(HTMLParser().unescape(env['content']), 50, striptags=True)

    def get_reply_mails(self):
        return MailReply.objects.filter(first=self).values_list('reply', flat=True)

    def set_thread(self, thread):
        self.thread = thread

    @staticmethod
    def get_valid_receiver(val):
        if isinstance(val, User):
            receiver = val
        else:
            #TODO: better code
            receiver_username = val
            if isinstance(val, str) or isinstance(val, unicode):
                c = Contact.objects.filter(email=val)
                if c:
                    receiver_username = c[0].username
                else:
                    receiver_username = receiver_username.split('@')[0]

            if isinstance(val, Contact):
                receiver_username = val.username
            try:
                receiver = User.objects.get(username=receiver_username)
            except User.DoesNotExist:
                receiver = None
        return receiver

    @staticmethod
    def validate_receiver(receiver):
        rc = Mail.get_valid_receiver(receiver)
        if rc:
            return True
        return False

    #@staticmethod
    def add_receiver(mail, thread, receiver_address, type='to', label_names=None, create_new_labels=True):
        """
        :param mail:
        :param thread:
        :param receiver_address: آدرس گیرنده
        :param type: to/cc/bcc نوع گیرنده، یکی از مقادیر
        :param label_names: نام برچسب‌هایی که این نامه در صندوق گیرنده به صورت پیش‌فرض خواهد داشت. پیش‌فرض آن تنها صندوق ورودی است.
        :param create_new_labels: آیا در صورت وجود نداشتن برچسب با نام مورد نظر، برچسبی جدید با همین نام برای این کاربر ایجاد بشود؟
        """
        if not label_names:
            label_names = []

        receiver = Mail.get_valid_receiver(receiver_address)
        if not receiver:
            logger.warn('Sending mail failed: user with username %s does not exists' % receiver_address)
            #TODO: send failed delivery report to sender
            return False

        label_names = set(label_names)  # unique
        if create_new_labels:
            labels = []
            for label_name in label_names:
                labels.append(Label.get_label_for_user(label_name, receiver, create_new=True))
        else:
            labels = Label.objects.filter(user=receiver, title__in=label_names)
        rc_labels = thread.get_user_labels(receiver)
        #TODO: I add create_new=True to next line
        rc_inbox = Label.get_label_for_user(Label.INBOX_LABEL_NAME, receiver,create_new=True)
        if len(labels) + rc_labels.count() == 0:
            labels = [rc_inbox]
        # Bug was! here: label is none and cause error in rest of the code
        for label in labels:
            thread.add_label(label)

        MailReceiver.objects.create(mail=mail, user=receiver, type=type)
        return True

    @staticmethod
    def create(content, subject, sender, receivers, cc=None, bcc=None, thread=None, titles=None,
               initial_sender_labels=None, attachments=None):
        """ یک نامه‌ی جدید می‌سازد و می‌فرستد

        :param content: متن نامه
        :type content: unicode
        :param subject: عنوان نامه
        :type subject: unicode
        :param sender: کاربر فرستنده
        :type sender: User
        :param receivers: آدرس دریافت کنندگان اصلی
        :type receivers: str[]
        :param cc: آدرس دریافت کنندگان رونوشت
        :type cc: str[]
        :param bcc: آدرس دریافت کنندگان مخفی
        :type bcc: str[]
        :param thread: نخ مربوطه که این نامه روی آن ارسال می‌شود، اگر از قبل وجود داشته باشد.
        :type thread: arsh.mail.models.Thread
        :param titles: نام برچسب‌هایی که این نامه پس از ارسال می‌گیرد. به صورت پیش‌فرض صندوق ورودی است.
        :type titles: str[]
        :rtype: arsh.mail.models.mail
        """

        recipients = {'to': receivers or [], 'cc': cc or [], 'bcc': bcc or []}
        recipients_users = []
        for t, rl in recipients.items():
            if rl and isinstance(rl[0], basestring) and ',' in rl[0]:
                #print 'RL must be a array!!!', rl
                rl = ','.join(rl).split(',')
            for r in rl:
                rc = Mail.get_valid_receiver(r)
                if not rc:
                    raise ValidationError(u"گیرنده نامعتبر است.")
                recipients_users.append(rc)
        if thread is None:
            logger.debug('creating new thread for mail')
            thread = Thread.objects.create(title=subject)

        # فقط میل‌هایی که کاربر شروع کرده در شاخه‌ی فرستاده شده‌هایش قرار می‌گیرد
        if not initial_sender_labels:
            initial_sender_labels = [Label.SENT_LABEL_NAME]
            #check mail as unread only if it is not in sent label
        if not 'unread' in initial_sender_labels and not Label.SENT_LABEL_NAME in initial_sender_labels:
            initial_sender_labels.append('unread')
        if sender:
            for label_name in initial_sender_labels:
                thread.add_label(Label.get_label_for_user(label_name, sender, True))
        else:
            logger.warn('sender in null, sending anonymous mail...')

        mail = Mail.objects.create(title=subject, thread=thread, created_at=datetime.datetime.now(), content=content,
                                   sender=sender)
        if attachments:
            for attached_file in attachments:
                mail.attachment_set.create(attachment=attached_file)

        if thread.firstMail is None:
            logger.debug('setting first thread mail')
            thread.firstMail = mail
            thread.save()

        logger.debug('mail saved')

        sent_count = 0
        recipients_count = 0
        for t, addresses in recipients.items():
            if addresses:
                for address in addresses:
                    if isinstance(address, str) or isinstance(address, unicode):
                        address = address.strip()
                    if not address:
                        continue
                    recipients_count += 1
                    sent = Mail.add_receiver(mail, thread, address, t, titles)
                    if sent:
                        sent_count += 1
        if sender and thread.has_label(Label.get_label_for_user(Label.REQUEST_LABEL_NAME, sender)):
            thread.set_new_request(recipients_users)

        logger.debug('mail sent to %d/%d of recipients' % (sent_count, recipients_count))
        return mail


    @staticmethod
    def reply(content, sender, receivers=None, cc=None, bcc=None, in_reply_to=None, subject=None, thread=None,
              include=[], exclude=[],
              titles=None, exclude_others=False,
              attachments=None):
        """ در پاسخ به یک نامه، یک میل جدید می‌فرستد.

        :param content: متن پاسخ
        :type content: unicode
        :param sender: فرستنده‌ی پاسخ
        :type sender: User
        :param receivers: آدرس دریافت کنندگان اصلی
        :type receivers: str[]
        :param cc: آدرس دریافت کنندگان رونوشت
        :type cc: str[]
        :param bcc: آدرس دریافت کنندگان مخفی
        :type bcc: str[]
        :param in_reply_to: این نامه پاسخ به کدام نامه است
        :type in_reply_to: Mail
        :param subject: عنوان نامه
        :type subject: unicode
        :param thread: نخ مربوطه
        :type thread: Thread
        :param include: کسانی که به گیرندگان اضافه می شوند
        :type include: str[]
        :param exclude: کسانی که از گیرندگان حذف می شوند
        :type exclude: str[]
        :param titles: نام برچسب‌هایی که این نامه پس از ارسال می‌گیرد. به صورت پیش‌فرض صندوق ورودی است.
        :type titles: str[]
        """
        #TODO: support adding to, cc,responders = None bcc in the middle of a thread

        to=""
        #in_reply_to = self
        if not thread and not in_reply_to:
            raise ValueError('No mail specified to reply to it!')
        if not thread:
            thread = in_reply_to.thread
        if not in_reply_to:
            in_reply_to = thread.get_last_mail()
            is_specific_reply = False
        else:
            is_specific_reply = True

        logger.debug('generating reply to mail#%d' % in_reply_to.id)
        mail = in_reply_to
        re_title = subject if subject else u'RE: ' + mail.title


        to = [mail.sender.username] if mail.sender.username != sender.username else []
        if receivers:
            to = to + receivers
        # else:
        #     to = [mail.sender.username] if mail.sender.username != sender.username else []
        if not exclude_others:
            for mr in MailReceiver.objects.filter(mail=mail):
                username = mr.user.username
                if not (
                                        username in to or username in cc or username in bcc or username in exclude or username == sender.username):
                    if mr.type == 'to':
                        to.append(username)
                    elif mr.type == 'cc':
                        cc.append(username)
                    elif mr.type == 'bcc':
                        bcc.append(username)
        for username in include:
            if not username in to:
                to.append(username)
        if len(to)==0:
            if len(cc)==0:
                if  len(bcc) == 0:
        #if (to==None) and (bcc==None) and (cc==None) :
                    logger.debug('no recipients can be selected to reply to, replying to sender')
                    to = [sender.username]
        reply = Mail.create(content, re_title, sender, receivers=to, cc=cc, bcc=bcc, thread=thread,
                            titles=titles, attachments=attachments)

        reply = Mail.create(content, re_title, sender, receivers=receivers, cc=cc, bcc=bcc, thread=thread,
                            titles=titles, attachments=attachments)

        # if is_specific_reply:
        MailReply.objects.create(first=in_reply_to, reply=reply)


    #@staticmethod


    def forward(self, content, sender, receivers, cc=None, bcc=None, in_reply_to=None, subject=None, thread=None,
              #include=[], exclude=[],
              titles=None,
              #exclude_others=False,
              attachments=None):
        """

        :param content: متن پاسخ
        :type content: unicode
        :param sender: فرستنده‌ی پاسخ
        :type sender: User
        :param receivers: آدرس دریافت کنندگان اصلی
        :type receivers: str[]
        :param cc: آدرس دریافت کنندگان رونوشت
        :type cc: str[]
        :param bcc: آدرس دریافت کنندگان مخفی
        :type bcc: str[]
        :param in_reply_to: این نامه پاسخ به کدام نامه است
        :type in_reply_to: Mail
        :param subject: عنوان نامه
        :type subject: unicode
        :param thread: نخ مربوطه
        :type thread: Thread
        :param include: کسانی که به گیرندگان اضافه می شوند
        :type include: str[]
        :param exclude: کسانی که از گیرندگان حذف می شوند
        :type exclude: str[]
        :param titles: نام برچسب‌هایی که این نامه پس از ارسال می‌گیرد. به صورت پیش‌فرض صندوق ورودی است.
        :type titles: str[]
        """
        #TODO: support adding to, cc,responders = None bcc in the middle of a thread

        to = ""
        in_reply_to = self
        #if not thread and not in_reply_to:
        #    raise ValueError('No mail specified to forward!')
        if not thread:
            thread = in_reply_to.thread
        if not in_reply_to:
            in_reply_to = thread.get_last_mail()
            #is_specific_reply = False
        #else:
            #is_specific_reply = True

        logger.debug('generating forward  mail#%d' % in_reply_to.id)
        #mail = in_reply_to
        mail = self
        re_title = subject if subject else u'FWD: ' + mail.title

        #TODO: attachment strategy should be fixed
        reply = Mail.create(content, re_title, sender, receivers=receivers, cc=cc, bcc=bcc, thread=thread,
                            titles=titles, attachments=self.attachment_set+attachments)


        # if is_specific_reply:
        #TODO: ask what is specific_reply?
        MailReply.objects.create(first=in_reply_to, reply=reply)

    def add_label(self, label):
        if not self.has_label(label):
            return ThreadLabel.add(label=label, thread=self.thread, mail=self)
        else:
            return False

    def remove_label(self, label):
        ThreadLabel.remove(label=label, thread=self.thread, mail=self)

    def has_label(self, label):
        return ThreadLabel.has_label(label=label, mail=self)

    def get_user_labels(self, user):
        qs = ThreadLabel.get_mail_labels(user=user, thread=self.thread, mail=self)
        return qs


def get_file_path(instance, filename):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    return "uploads/attachments/%s/%s/%s" % (instance.mail.sender.username, now, filename)


class Attachment(models.Model):
    mail = models.ForeignKey(Mail)
    attachment = models.FileField(upload_to=get_file_path, verbose_name=u'فایل ضمیمه', null=True, blank=True)


#TODO: implement this in show_thread, etc.
class MailReply(models.Model):
    class Meta:
        verbose_name=u"پاسخ میل"
        verbose_name_plural=u"پاسخ‌های میل"

    first = models.ForeignKey(Mail, related_name='+')
    reply = models.ForeignKey(Mail, related_name='+')


class MailReceiver(models.Model):
    TYPE_CHOICES = (('to', 'to'),
                    ('cc', 'cc'),
                    ('bcc', 'bcc'), )
    mail = models.ForeignKey(Mail)
    user = models.ForeignKey(User)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    def __unicode__(self):
        return self.mail.title + "  " + self.user.first_name

    def save(self, *args, **kwargs):
        new = False
        if self.id is None:
            new = True
        models.Model.save(self, *args, **kwargs)
        user_mails = self.mail.thread.get_user_mails(self.user)
        #thread is marked as unread only if thread was not related to user until now
        if new and len(user_mails) <= 1:
            self.mail.thread.mark_as_unread(self.user)
        #this case is for mails which are sent in threads related to user(ex: as reply)
        else:
            self.mail.thread.mark_as_unread(self.user, mails=[self.mail])


class Label(Slugged):
    u""" این مدل یک برچسب را نشان می‌دهد. هر برچسب وابسته به یک کاربر است و برچسب‌های
        کاربران مختلف، حتی اگر نام این برچسب‌ها یکی باشند، متفاوت هستند.
    """

    class Meta:
        verbose_name = u"برچسب"
        verbose_name_plural = u"برچسب‌ها"

    INBOX_LABEL_NAME = u'صندوق ورودی'
    CHAT_LABEL_NAME = u'چت'
    SENT_LABEL_NAME = u'فرستاده شده'
    UNREAD_LABEL_NAME = u'unread'
    TRASH_LABEL_NAME = u'زباله دان'
    SPAM_LABEL_NAME = u'هرزنامه'
    ARCHIVE_LABEL_NAME = u'بایگانی'
    STARRED_LABEL_NAME = u'مهم'
    TODO_LABEL_NAME = u'کارها'
    COMPLETED_LABEL_NAME = u'کارها/انجام شده'
    REQUEST_LABEL_NAME = u'درخواست ها'

    # TODO: this may be different in different accounts
    STD_LABELS = {
        'inbox': INBOX_LABEL_NAME,
        'chat': CHAT_LABEL_NAME,
        'sent': SENT_LABEL_NAME,
        'unread': UNREAD_LABEL_NAME,
        'trash': TRASH_LABEL_NAME,
        'spam': SPAM_LABEL_NAME,
        'archive': ARCHIVE_LABEL_NAME,
        'starred': STARRED_LABEL_NAME,
        'todo': TODO_LABEL_NAME,
        'completed': COMPLETED_LABEL_NAME,
        'request': REQUEST_LABEL_NAME,
    }
    INITIAL_LABELS = (INBOX_LABEL_NAME, SENT_LABEL_NAME, UNREAD_LABEL_NAME,  STARRED_LABEL_NAME,
                      TRASH_LABEL_NAME, SPAM_LABEL_NAME, ARCHIVE_LABEL_NAME, REQUEST_LABEL_NAME, )

    account = models.ForeignKey(MailAccount, related_name='labels')
    user = models.ForeignKey(User, related_name='labels')  # delete with data migration
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return self.title

    def get_std_name(self):
        for k, v in self.STD_LABELS.iteritems():
            if v == self.title:
                return k
        return ''

    def is_initial_label(self):
        return self.get_std_name() != ''

    # @property
    # def user(self):
    #     return self.account.user

    def delete_this(self):
        if self.is_initial_label():
            raise ValueError
        self.delete()

    @staticmethod
    def create(user, title, account=None):
        if account is None:
            try:
                account = user.mail_accounts.all()[0]
            except IndexError:
                account = MailAccount.objects.create(user=user, provider=MailProvider.get_default_provider(),
                                                     email=user.username + '@' + MailProvider.get_default_domain())
        return Label.objects.create(title=title, user=user, account=account)

    def get_unread_count(self):
        """ برای این برچسب (و کاربر متناظر با آن)، تعداد نخ‌هایی که حداقل یک نامه‌ی خوانده
        نشده دارند را می‌دهد.
        :return: تعداد نخ‌های خوانده نشده
        :rtype: int
        """
        from .UserManager import UserManager

        unread_label = UserManager.get(self.user).get_unread_label()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM user_mail_threadlabel tl
            WHERE
                tl.label_id={label1}
              AND
                (
                  SELECT COUNT(*)
                  FROM user_mail_threadlabel tl2
                  WHERE tl2.label_id={label2} AND tl2.thread_id=tl.thread_id
                )>0
        """.format(label1=unread_label.id, label2=self.id))
        row = cursor.fetchone()
        return row[0]

    def limited_labels(self):
        return self.title in [self.TRASH_LABEL_NAME, self.SPAM_LABEL_NAME]

    @staticmethod
    def get_label_for_user(label_name, user, create_new=False):
        u""" با دادن نام برچسب، شی برچسب متناظر برای کاربر مد نظر را می‌دهد.

        :param label_name: نام برچسب
        :type label_name: str or unicode
        :param user: کاربر مد نظر
        :type user: django.contrib.auth.models.User
        :param create_new: در صورت عدم وجود چنین برچسبی، آیا ساخته بشود؟
        :type create_new: bool
        :return: برچسب
        :rtype: Label or None
        """

        try:
            return Label.objects.get(title=label_name, user=user)
        except Label.DoesNotExist:
            if create_new:
                return Label.create(title=label_name, user=user)
            return None

    @classmethod
    def get_initial_labels(cls):
        return cls.INITIAL_LABELS

    @classmethod
    def get_label_ordering_func(cls):
        def order(label):
            """
                :type label: Label
            """
            try:
                return cls.INITIAL_LABELS.index(label.title), ''
            except ValueError:
                return len(cls.INITIAL_LABELS), label.title
        return order

    @staticmethod
    def setup_initial_labels(user):
        u""" برچسب‌های اولیه‌ی لازم برای کارایی سیستم را برای کاربر داده شده مي سازد. این
            عمل چند پرسمان در پایگاه داده انجام می‌دهد و در نتیجه تنها باید در موقع نیاز فراخوانی
            بشود.

        :param user: کاربر مورد نظر
        :rtype user: django.contrib.auth.models.User
        :return: None
        """
        labels = Label.get_initial_labels()
        for label in labels:
            if not Label.objects.filter(title=label, user=user).count():
                Label.create(title=label, user=user)

    @staticmethod
    def get_user_labels(user):
        """ تمام برچسب‌های مربوط به کاربر داده شده را برمی‌گرداند. برچسب‌های صرفا مجازی
            که تنها برای عملکرد داخلی سیستم به کار می‌رود، مانند خوانده نشده، برگردانده نمی‌شوند.

        :param user: کاربر مورد نظر یا آی‌دی کاربر
        :type user: django.contrib.auth.models.User or int
        :return: تمام برچسب‌های این کاربر
        :rtype: QuerySet of Label
        """
        if isinstance(user, User):
            user = user.id
        return Label.objects.filter(user__id=user).exclude(title=Label.UNREAD_LABEL_NAME)

    @classmethod
    def parse_label_title(cls, title):
        if title == 'trash':
            return cls.TRASH_LABEL_NAME
        elif title == 'spam':
            return cls.SPAM_LABEL_NAME
            #TODO: complete this
        return None


class Thread(Slugged):
    class Meta:
        verbose_name = u"نخ"
        verbose_name_plural = u"نخ‌ها"

    title = models.CharField(max_length=255)
    firstMail = models.ForeignKey(Mail, null=True, related_name='headThread')
    labels = models.ManyToManyField(Label, through='ThreadLabel', related_name='threads')
    #TODO : Implement -> Starred Thread , approved , and in-progress thread

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Thread, self).save(*args, **kwargs)

    def add_label(self, label):
        if not self.has_label(label):
            #noinspection PyUnresolvedReferences
            return ThreadLabel.add(label=label, thread=self)
        else:
            return False

    def remove_label(self, label):
        #noinspection PyUnresolvedReferences
        ThreadLabel.remove(label=label, thread=self)

    def has_label(self, label):
        return label in self.labels.all()

    def get_user_labels(self, user, remove_special_labels=True):
        qs = self.labels.filter(user=user)
        if remove_special_labels:
            qs = qs.exclude(title='unread')
        return qs

    def is_unread(self, user=None):
        from .UserManager import UserManager

        return self.has_label(UserManager.get(user).get_unread_label())

    def mark_as_read(self, user=None):
        from .UserManager import UserManager

        ReadMail.mark_as_read(user, self.mails.all())
        return self.remove_label(UserManager.get(user).get_unread_label())

    def mark_as_unread(self, user=None, mails=None):
        from .UserManager import UserManager

        unread = mails
        if not unread:
            unread = self.mails.all()
        ReadMail.mark_as_unread(user, unread)
        return self.add_label(UserManager.get(user).get_unread_label())

    def get_last_mail(self):
        """ آخرین نامه‌ی این نخ را برمی‌گرداند

            :raises: Mail.DoesNotExist
            :return: آخرین میل این نخ
            :rtype: Mail
        """
        return self.mails.order_by('-created_at')[0:1].get()

    def get_sorted_mails(self):
        """نامه های این نخ را بر می گرداند.

            :raises: Mail.DoesNotExist
            :return: آخرین میل این نخ
            :rtype: QuerySet of Mail
        """
        return self.mails.order_by('-created_at')

    def get_unread_mails(self, user):
        #Query No: 1 for each iteration!
        #TODO: improve (probably with joining tables)
        mails = [mail for mail in self.get_user_mails(user) if not ReadMail.has_read(user, mail)]
        #mails =
        return mails

    def is_thread_related(self, user):
        u"""
        یک کاربر به عنوان ورودی میگیرد و بررسی میکند آیا این
         کاربر در لیست افراد مرتبط با ترد (گیرندگان یا فرستندگان نامه های ترد)
          قرار دارد یا خیر.
        :param user: کاربر
        :type user User

        :rtype: int or None
        :return:اگر کاربر در لیست افراد مرتبط با ترد وجود داشت آی دی آن را بر میگرداند.
        """
        #Query No: 0
        related_users = []
        for mail in self.mails.all():
            for r in mail.recipients.all():
                if r.id not in related_users:
                    related_users += [r.id]
        if self.firstMail.sender_id not in related_users:
            related_users += [self.firstMail.sender_id]
        return user.id in related_users

    def get_user_mails(self, user):
        """
        از ترد جاری تمام ایمیلهای مربوط به کاربر ورودی را برمیگرداند
        :param user: کابر
        :type user: User
        :rtype list of Mail ojects
        :return:لیست میل هایی از ترد که مرتبط با کاربر است
        """

        #Query No: 0
        mail_list = Mail.objects.filter(thread=self, (recipients_contains=user | sender=user)).distinct()

        #mail_list = []
        #for mail in self.mails.all():
        #    if mail.sender_id == user.id or user in mail.recipients.all():
        #        if mail not in mail_list:
        #            mail_list.append(mail)
        return mail_list

    def get_participants(self, related_user=None):
        thread_mails = self.mails.all()

        if related_user:
            thread_mails = thread_mails.filter(sender=related_user) | thread_mails.filter(recipients=related_user)

        sender_ids = thread_mails.values_list('sender', flat=True).distinct()
        #senders = User.objects.filter(id__in=sender_ids)

        recipient_ids = thread_mails.values_list('recipients', flat=True).distinct()
        participant_ids= sender_ids + recipient_ids

        #recipients = User.objects.filter(id__in=recipient_ids)
        participants = User.objects.filter(id__in=participant_ids)

        return {'participants': participants}

    def get_senders(self, related_user=None):
        thread_mails = self.mails.all()

        if related_user:
            thread_mails = thread_mails.filter(sender=related_user) | thread_mails.filter(recipients=related_user)

        sender_ids = thread_mails.values_list('sender', flat=True).distinct()
        senders = User.objects.filter(id__in=sender_ids)


        return {'senders': senders}

    def get_receivers(self, related_user=None):
        thread_mails = self.mails.all()

        if related_user:
            thread_mails = thread_mails.filter(sender=related_user) | thread_mails.filter(recipients=related_user)


        recipient_ids = thread_mails.values_list('recipients', flat=True).distinct()
        recipients = User.objects.filter(id__in=recipient_ids)

        return {'recipients': recipients}



    def complete_todo(self):
        ls = self.get_participants()
        #p_all = ls['senders'] | ls['recipients']
        #for p in p_all:
        for p in ls:
            self.add_label(Label.get_label_for_user(Label.COMPLETED_LABEL_NAME, p, create_new=True))

    def set_new_request(self, new_recipients):
        """
          آماده سازی ترد به صورت یک درخواست.
          تمامی گیرندگان جدید باید به میل های قبلی ترد
          اضافه شوند و این ترد در برچسب درخواست آنها وارد شود.
        :return:None
        """

        for mail in self.mails.all():
            for r in new_recipients:
                if not r == mail.sender and not r in mail.recipients.all():
                    Mail.add_receiver(mail, self, r, type='cc', label_names=[Label.REQUEST_LABEL_NAME],
                                      create_new_labels=True)

    def get_deadline(self):
        import re
        #TODO:check this search
        mail=self.firstMail
        sub = re.search(re.compile(ur'\u0645\u0647\u0644\u062a \u0627\u0646\u062c\u0627\u0645:(.)+', re.U),
                        mail.content)
        if sub:
            try:
                d_str = sub.group(0).split(':')
                days = d_str[1].split(u'\u0631\u0648\u0632')
                if days:
                    d = days[0]
                    sd = mail.created_at.date()
                    deadline = sd + datetime.timedelta(days=int(d))
                    return deadline
            except Exception:
                return None

    @staticmethod
    def get_user_threads(user):
        return Thread.objects.filter(labels__user=user)


class ThreadLabel(models.Model):

    thread = models.ForeignKey(Thread)
    label = models.ForeignKey(Label)
    mails = models.ManyToManyField(Mail, null=True, blank=True)

    class Meta:
        verbose_name = u"برچسب نخ"
        verbose_name_plural = u"برچسب‌های نخ"

    @classmethod
    def add(cls, label, thread, mail=None):
        try:
            tl = cls.objects.get(label=label, thread=thread)
            if mail and tl.mails.all():
                #برچسب متعلق به کل نخ نباشد
                ##  #خود تابع بررسی میکند اگر قبلا موجود نباشد، آن را اضافه میکند
                tl.mails.add(mail)
                return True

            else:
            #کل نخ برچسب خورده و امکان برچسب زدن به یکی از ایمیلهای آن نیست
                return False

        except cls.DoesNotExist:
            new_record = cls.objects.create(label=label, thread=thread)
            if mail:
                new_record.mails.add(mail)
            return True

    @classmethod
    def remove(cls, label, thread, mail=None):
        try:
            tl = cls.objects.get(label=label, thread=thread)
        except cls.DoesNotExist:
            return False

        if mail:
            if mail in tl.mails.all():
                tl.mails.remove(mail)
                if not tl.mails.all():
                    tl.delete()
                return True
        else:
            tl.delete()
            return True

    @classmethod
    def has_label(cls, label, mail):
        try:
            tl = cls.objects.get(label=label, thread=mail.thread)
        except cls.DoesNotExist:
            return False
        if tl.mails.all() and mail in tl.mails.all():
            return True
        else:
            return False

    @classmethod
    def get_mail_labels(cls, user, thread, mail):
        qs = cls.objects.filter(label__user=user, thread=thread, mails=mail)
        return qs


class AddressBook(models.Model):
    class Meta:
        verbose_name = u"دفتر آدرس"
        verbose_name_plural = u"دفترهای آدرس"

    user = models.OneToOneField(User)

    def get_all_contacts(self):
        u"""

        :rtype: List
        :return: لیستی از نام های قابل نمایش مخاطبین بر می گرداند.
        """

        return Contact.objects.filter(address_book=self)

    def has_contact(self, contact):
        """
        بررسی میکند که تماس داده شده
        در این لیست وجود دارد یا نه.

        :type contact: Contact
        :return: bool
        """
        if not contact:
            return False
        if self.get_all_contacts().filter(id=contact.id):
            return True
        return False

    def has_contact_address(self, address):
        """
        بررسی میکند آیا تماسی با آدرس داده شده
        در لیست نشانی ها وجود دارد یا نه.
        :type address: unicode
        :return: bool
        """
        c = Contact.get_contact_by_address(address, book=self)
        if c:
            return True
        return False

    def add_contact_by_user(self, contact_user):
        u'''
کاربر داده شده را به مخاطبین اضافه می کند، و فیلدهای مربوط به مخاطب را با توجه به مقادیر کاربر داده شده مقداردهی می کند.
        :type contact_user: User
        :param contact_user: کاربری که می خواهیم به مخاطبین افزوده شود.

        :rtype: Contact
        :return: مخاطب ساخته شده را برمی گرداند

        :raise: ValueError
        '''

        try:
            #if contact_user == self.user:
            #    raise ValueError(u"آدرس شما نمیتواند به لیست اضافه شود.")
            if self.has_contact_address(contact_user.username + '@' + MailProvider.get_default_domain()):
                raise ValueError(u"این آدرس  قبلا به لیست اضافه شده است.")
            else:
                raise Contact.DoesNotExist
        except Contact.DoesNotExist:
            return Contact.objects.create(address_book=self, display_name=contact_user.get_full_name(),
                                          first_name=contact_user.first_name, last_name=contact_user.last_name,
                                          email=contact_user.username + '@' + MailProvider.get_default_domain())


    @staticmethod
    def get_addressbook_for_user(user, create_new=False):
        u'''
        دفتر نشانی کاربر داده شده را برمی گرداند و در صورت نیاز یک دفتر نشانی جدید می سازد.
        :type user: User
        :param user: کاربری که می خواهیم دفتر آدرس را برای آن بردانیم.

        ::type create_new: Bool
        :param create_new: در صورت پیدا نکردن دفتر نشانی برای کاربر یک دفتر نشانی می سازد.

        :rtype: AddressBook or None
        :return: دفتر نشانی پیدا شده و یا ساخته شده را برمی گرداند.
        '''

        try:
            return AddressBook.objects.get(user=user)
        except AddressBook.DoesNotExist:
            if create_new:
                return AddressBook.objects.create(user=user)
            return None

    def remove_contact_address(self, address):
        contact = Contact.objects.get(address_book=self, email=address)
        if contact:
            contact.delete()
            return True
        return False

    def remove_contact(self, contact):
        contact_d = Contact.objects.get(address_book=self, email=contact.email)
        if contact:
            contact.delete()
            return True
        return False


class Contact(models.Model):

    address_book = models.ForeignKey(AddressBook)
    display_name = models.CharField(_('display_name'), max_length=30, blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True, null=True)
    email = models.CharField(_('e-mail address'), max_length=30)
    additional_email = models.EmailField(_('e-mail address'), blank=True, null=True)

    class Meta:
        verbose_name = u"اطلاعات تماس‌ها"
        verbose_name_plural = u"اطلاعات تماس"

    def __unicode__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.email
        super(Contact, self).save(*args, **kwargs)

    def get_display_name(self):
        if self.display_name:
            return self.display_name
        return self.email

    @property
    def username(self):
        return self.email.split('@')[0]

    @classmethod
    def get_contact_by_address(cls, address, book=None):
        """
        در صورت وجود، تماس با آدرس
        داده شده را برمیگرداند.
        :type address: str
        :return: Contact or None
        """
        if book:
            c = cls.objects.filter(email=address, address_book=book)
        else:
            c = cls.objects.filter(email=address)
        return c


class ReadMail(models.Model):

    mail = models.ForeignKey(Mail, blank=False)
    reader = models.ForeignKey(User, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def has_read(user, mail):
        #Query No:1
        try:
            ReadMail.objects.get(mail=mail, reader=user)
        except ReadMail.DoesNotExist:
            return True
        return False

    @staticmethod
    def mark_mails(user, mails):
        for mail in mails:
            if ReadMail.has_read(user, mail):
                mail.status = ' read'
            else:
                mail.status = ' unread'

    @staticmethod
    def mark_as_read(user, mails):
     #, respond=False):
        unread = len(mails)
        for mail in mails:
            if not ReadMail.has_read(user, mail):
                ReadMail.objects.get(reader=user, mail=mail).delete()
            unread -= 1
        return unread

    @staticmethod
    def mark_as_unread(user, mails, respond=False):
        read = len(mails)
        for mail in mails:
            if ReadMail.has_read(user, mail):
                raw_content = mail.content
                index = raw_content.rfind(FOOTER_SLUG)
                if index != -1 and not respond:
                    continue
                ReadMail.objects.create(reader=user, mail=mail)
            read -= 1
        return read
