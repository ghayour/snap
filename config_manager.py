# -*- coding: utf-8 -*-
from django.conf import settings

from arsh.common.patterns.basic import Singleton


class ConfigManager(Singleton):
    SETTINGS_VARIABLE = 'USER_MAIL_CONFIG'
    DEFAULT_CONFIG = {
        'default-view': 'new',
        'inbox-folder': u'کاربران',
        'system-state': 'requests',
    }

    def __init__(self):
        try:
            self.config = getattr(settings, self.SETTINGS_VARIABLE)
        except AttributeError:
            self.config = {}
        for k, v in self.DEFAULT_CONFIG.iteritems():
            if not k in self.config:
                self.config[k] = v

    def get(self, key):
        return self.config[key]
