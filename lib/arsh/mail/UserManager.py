# -*- coding: utf-8 -*-
from django.contrib.auth.models            import User

from arsh.mail.Manager                     import DecoratorManager
from arsh.mail.models                      import Label




class UserManager:
    _instance = None

    @staticmethod
    def get(*args, **kwargs):
        """
        :rtype: UserManager
        :return:singleton UserManager
        """
        if UserManager._instance is None:
            UserManager._instance = UserManager(*args, **kwargs)
            return UserManager._instance
        UserManager._instance.reload(*args, **kwargs)
        return UserManager._instance


    def __init__(self, user):
        self.load(user)
        self._register_hooks()


    def _register_hooks(self):
        #Register plugin hooks here
        pass


    def reload(self, user=None):
        if self._user != user:
            self.load(user)

    def load(self, user=None):
        self._user = user
        self._unread_label = None
        self._cached_users = set()

    def setup_mailbox(self):
        Label.setup_initial_labels(self._user)

    def get_label(self, label_name):
        """
        1 Query

            :rtype: rezgh.mail.models.Label
        """
        try:
            return Label.objects.get(title = label_name, user = self._user)
        except Label.DoesNotExist:
            return None

    def get_inbox(self):
        """
            :rtype: rezgh.mail.models.Label
        """
        return self.get_label(Label.INBOX_LABEL_NAME)


    def get_unread_label(self):
        if self._unread_label is None:
            self._unread_label = self.get_label(Label.UNREAD_LABEL_NAME)
        return self._unread_label

    def _cache_user(self, user):
        self._cached_users.add(user)

    def get_user(self, id):
        for user in self._cached_users:
            if user.id == id:
                return user

        user = User.objects.get(id=id)
        self._cache_user(user)
        return user
