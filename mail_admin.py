# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from arsh.common.patterns.basic import Singleton
from arsh.user_mail.models import MailAccount, MailProvider


class MailAdmin(Singleton):
    @classmethod
    def prepare(cls, *args, **kwargs):
        """
            :return: Singleton instance
            :rtype: MailAdmin
        """
        return super(MailAdmin, cls).prepare(*args, **kwargs)

    def user_has_mail_account(self, user):
        """ آیا این کاربر حساب میلی در سیستم برایش ثبت شده است؟

            :param User user: django user
            :rtype: bool
        """
        return user.mail_accounts.all().count() > 0

    def create_arsh_mail_account(self, user):
        MailAccount.objects.create(user=user, provider=MailProvider.get_default_provider(),
                                   email=user.username + '@' + MailProvider.get_default_domain())

    def get_user(self, username, domain=None, ensure_mail_account=False):
        """

            :rtype: User
        """
        if domain is None:
            try:
                username, domain = username.split('@')
            except ValueError:
                raise ValueError('Either domain must be specified or username must have @')

        if domain != 'arshmail.ir':
            raise ValueError('User creation not supported for external domains: {0}'.format(domain))

        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            u = User.objects.create(username=username, password='!arsh-login')

        if ensure_mail_account:
            if not self.user_has_mail_account(u):
                self.create_arsh_mail_account(u)
        return u
