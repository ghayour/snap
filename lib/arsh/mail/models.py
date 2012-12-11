# -*- coding: utf-8 -*-
import datetime
import logging

from django.db                             import models
from django.contrib.auth.models            import User

from arsh.db_models.common                 import Slugged
from arsh.text.utils                       import get_summary

from arsh.mail.Manager                     import DecoratorManager
from arshlib__user_mail.mail.urls          import urlpatterns
from django.core.urlresolvers              import resolve



__docformat__ = 'reStructuredText'
logger = logging.getLogger()



class Mail(models.Model):
    sender = models.ForeignKey(User, related_name='sender', verbose_name=u'فرستنده')
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
        env = {'content': self.content}
        DecoratorManager.get().activate_hook('get_mail_summary', env, self)
        return get_summary(env['content'], 50, striptags=True)


    def set_thread(self, thread):
        self.thread = thread


    @staticmethod
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

        if isinstance(receiver_address, User):
            receiver = receiver_address
        else:
            try:
                receiver = User.objects.get(username=receiver_address)
            except User.DoesNotExist:
                logger.warn('Sending mail failed: user with username %s does not exists' % receiver_address)
                #TODO: send failed delivery report to sender
                return False

        label_names = set(label_names) #unique
        if create_new_labels:
            labels = []
            for label_name in label_names:
                labels.append(Label.get_label_for_user(label_name, receiver, create_new=True))
        else:
            labels = Label.objects.filter(user=receiver, title__in=label_names)
        if len(labels) + thread.get_user_labels(receiver).count() == 0:
            labels = [Label.get_label_for_user(Label.INBOX_LABEL_NAME, receiver)]
        for label in labels:
            thread.add_label(label)

        MailReceiver.objects.create(mail=mail, user=receiver, type=type)
        return True


    @staticmethod
    def create(content, subject, sender, receivers, cc=None, bcc=None, thread=None, titles=None,
               initial_sender_labels=None):
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
        :type thread: rezgh.mail.models.Thread
        :param titles: نام برچسب‌هایی که این نامه پس از ارسال می‌گیرد. به صورت پیش‌فرض صندوق ورودی است.
        :type titles: str[]
        :rtype: rezgh.mail.models.mail
        """
        #        Label.setup_initial_labels(sender)
        #        Label.setup_initial_labels(User.objects.get(id=1))
        if thread is None:
            logger.debug('creating new thread for mail')
            thread = Thread.objects.create(title=subject)

        # فقط میل‌هایی که کاربر شروع کرده در شاخه‌ی فرستاده شده‌هایش قرار می‌گیرد
        if not initial_sender_labels:
            initial_sender_labels = [Label.SENT_LABEL_NAME]
        if not 'unread' in initial_sender_labels:
            initial_sender_labels.append('unread')
        if sender:
            for label_name in initial_sender_labels:
                thread.add_label(Label.get_label_for_user(label_name, sender, True))
        else:
            logger.warn('sender in null, sending anonymous mail...')

        mail = Mail.objects.create(title=subject, thread=thread, created_at=datetime.datetime.now(), content=content,
            sender=sender)

        if thread.firstMail is None:
            logger.debug('setting first thread mail')
            thread.firstMail = mail
            thread.save()

        logger.debug('mail saved')

        sent_count = 0
        recipients_count = 0
        recipients = {'to': receivers, 'cc': cc, 'bcc': bcc}
        for t, addresses in recipients.items():
            if addresses:
                for address in addresses:
                    if isinstance(address, str) or isinstance(address, unicode):
                        address = address.strip()
                    if not address: continue
                    recipients_count += 1
                    sent = Mail.add_receiver(mail, thread, address, t, titles)
                    if sent: sent_count += 1

        logger.debug('mail sent to %d/%d of recipients' % (sent_count, recipients_count))
        return mail


    @staticmethod
    def reply(content, sender, in_reply_to=None, thread=None):
        """ در پاسخ به یک نامه، یک میل جدید می‌فرستد.

        :param content: متن پاسخ
        :type content: unicode
        :param sender: فرستنده‌ی پاسخ
        :type sender: User
        :param in_reply_to: این نامه پاسخ به کدام نامه است
        :type in_reply_to: Mail
        :param thread: نخ مربوطه
        :type thread: Thread
        """
        #TODO: support adding to, cc,responders = None bcc in the middle of a thread

        if not thread and not in_reply_to:
            raise ValueError('No mail specified to reply to it!')
        if not thread: thread = in_reply_to.thread
        if not in_reply_to: in_reply_to = thread.get_last_mail()

        logger.debug('generating reply to mail#%d' % in_reply_to.id)
        mail = in_reply_to
        to = [mail.sender.username] if mail.sender != sender else []
        cc = []
        bcc = []
        for mr in MailReceiver.objects.filter(mail=mail):
            if mr.user == sender:
                continue
            if mr.type == 'to':
                to.append(mr.user.username)
            elif mr.type == 'cc':
                cc.append(mr.user.username)
            elif mr.type == 'bcc':
                bcc.append(mr.user.username)
        if len(to) + len(cc) + len(bcc) == 0:
            logger.debug('no recipients can be selected to reply to, replying to sender')
            to = [sender.username]
        Mail.create(content, mail.title, sender, receivers=to, cc=cc, bcc=bcc, thread=thread)



#TODO: implement this in showThread, etc.
class MailReply(models.Model):
    first = models.ForeignKey(Mail, related_name='+')
    reply = models.ForeignKey(Mail, related_name='+')


class MailReceiver(models.Model):
    TYPE_CHOICES = (('to', 'to'),
                    ('cc', 'cc'),
                    ('bcc', 'bcc'),
        )
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
        if new:
            self.mail.thread.mark_as_unread(self.user)


class Label(Slugged):
    u""" این مدل یک برچسب را نشان می‌دهد. هر برچسب وابسته به یک کاربر است و برچسب‌های
        کاربران مختلف، حتی اگر نام این برچسب‌ها یکی باشند، متفاوت هستند.
    """

    INBOX_LABEL_NAME = u'صندوق ورودی'
    SENT_LABEL_NAME = u'فرستاده شده'
    UNREAD_LABEL_NAME = u'unread'

    user = models.ForeignKey(User, related_name='labels')
    title = models.CharField(max_length=50)


    def __unicode__(self):
        return self.title


    def get_unread_count(self):
        """ برای این برچسب (و کاربر متناظر با آن)، تعداد نخ‌هایی که حداقل یک نامه‌ی خوانده
        نشده دارند را می‌دهد.
        :return: تعداد نخ‌های خوانده نشده
        :rtype: int
        """
        from arsh.mail.UserManager import UserManager
        return self.threads.filter(labels=UserManager.get(self.user).get_unread_label()).count()


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
                return Label.objects.create(title=label_name, user=user)
            return None


    @staticmethod
    def setup_initial_labels(user):
        u""" برچسب‌های اولیه‌ی لازم برای کارایی سیستم را برای کاربر داده شده مي سازد. این
            عمل چند پرسمان در پایگاه داده انجام می‌دهد و در نتیجه تنها باید در موقع نیاز فراخوانی
            بشود.

        :param user: کاربر مورد نظر
        :rtype user: django.contrib.auth.models.User
        :return: None
        """
        labels = [Label.INBOX_LABEL_NAME, Label.SENT_LABEL_NAME, Label.UNREAD_LABEL_NAME]
        for label in labels:
            if not Label.objects.filter(title=label, user=user).count():
                Label.objects.create(title=label, user=user)

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



class Thread(Slugged):
    title = models.CharField(max_length=255)
    firstMail = models.ForeignKey(Mail, null=True, related_name='headThread')
    labels = models.ManyToManyField(Label, related_name='threads')
    #TODO : Implement -> Starred Thread , approved , and in-progress thread

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Thread, self).save(*args, **kwargs)


    def add_label(self, label):
        if not label in self.labels.all():
            #noinspection PyUnresolvedReferences
            self.labels.add(label)

    def remove_label(self, label):
        #noinspection PyUnresolvedReferences
        self.labels.remove(label)

    def has_label(self, label):
        return label in self.labels.all()


    def get_user_labels(self, user, remove_special_labels=True):
        qs = self.labels.filter(user=user)
        if remove_special_labels:
            qs = qs.exclude(title='unread')
        return qs

    def is_unread(self, user=None):
        from arsh.mail.UserManager import UserManager
        return self.has_label(UserManager.get(user).get_unread_label())

    def mark_as_read(self, user=None):
        from arsh.mail.UserManager import UserManager
        return self.remove_label(UserManager.get(user).get_unread_label())

    def mark_as_unread(self, user=None):
        from arsh.mail.UserManager import UserManager
        return self.add_label(UserManager.get(user).get_unread_label())

    def get_last_mail(self):
        """ آخرین نامه‌ی این نخ را برمی‌گرداند

            :raises: Mail.DoesNotExist
            :return: آخرین میل این نخ
            :rtype: Mail
        """
        return self.mails.order_by('-created_at')[0:1].get()

    @staticmethod
    def get_user_threads(user):
        return Thread.objects.filter(labels__user=user)

def Test_creator(url_string=None):
    """
    :param url_string:
    :return:
    یک اسکلت مناسب برای ایجاد تست تولید می کند. ورودی به صورت رشته url ها است.
    فرض بر این استه که باید لاگین صورت پذیرد. این کار با یوزر admin و پسورد admin صورت می گیرد.
    """
    print urlpatterns
    result = 'calss AppTest(TestCase): \n'
    result += '\tfixtures = [\'auth\']\n'
    result += '\tdef setUp(self):\n'
    result += '\t\tself.client = Client()\n'
    result += '\t\tself.assertTrue(self.client.login(username=\'admin\',password=\'admin\'))\n'
    for pattern in url_string:
        temp = str(pattern)
        temp = temp.replace('<RegexURLPattern ','')
        temp = temp.replace('>','')
        list = temp.split(' ')
        temp = list[0]
        temp2 = list[0].replace('/',' ')
        temp2 = temp2.title()
        temp2 = temp2.replace(' ','_')
        temp2.capitalize()
        result += '\tdef test'+temp2 + ':\n'
        result += '\t\tresponse = self.client.get(\''+temp+'\')\n'
        result += '\t\tself.assertEqual(response.status_code,200)\n'
        result += '\t\tself.assertTemplateUsed(response,\'\')\n'
    with open("Output.txt","wb") as Textfile:
        Textfile.write(result)
    #TODO: RegexURLPattern object must be analysed...


Test_creator(urlpatterns)
