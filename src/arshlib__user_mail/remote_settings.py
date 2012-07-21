# -*- coding: utf-8 -*-

from project_name import *

DEBUG          = False
DAJAXICE_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG


LOGGING = {
    'loggers': {
        '': {
            'handlers': ['mail_admin', 'console'], # can be: null, console, mail_admin
            'level': 'WARNING',
            },
        '%s' % PROJECT_INSTANCE_NAME: {
            'handlers': ['console'], # can be: null, console, mail_admin
            'level': 'INFO',
            'propagate': True,
            },
    }
}


BASEPATH      = '/www/%s/'				% PROJECT_INSTANCE_NAME
STATIC_ROOT   = BASEPATH + '../static-roots/%s/' % PROJECT_INSTANCE_NAME
SITE_URL      = 'http://?/'
LOGIN_URL     = '/accounts/login/'
TEMPLATE_DIRS = (
	'/usr/local/lib/python2.7/dist-packages/django/contrib/admin/templates/',
)


SERVE_STATIC_FILES = False


SECRET_KEY    = '?' # ATTENTION: DON'T COMMIT THIS LINE


DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     '%s' % PROJECT_INSTANCE_NAME,
        'USER':     '%s' % PROJECT_INSTANCE_NAME,
		'PASSWORD': '?', # ATTENTION: DON'T COMMIT THIS LINE
        'HOST':     '',
        'PORT':     '',
    }
}

ADMINS = (
#    ('?',                    '?'),
    ('Arsh Server Admin',    'server@arsh.co.ir'),
)
