# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (Label, Thread, MailDomain, MailProvider, ProviderImapSettings,
                     ImapMailAccount, DatabaseMailAccount)


admin.site.register(MailDomain)
admin.site.register(MailProvider)
admin.site.register(ProviderImapSettings)
admin.site.register(ImapMailAccount)
admin.site.register(DatabaseMailAccount)

admin.site.register(Label)
admin.site.register(Thread)
