# -*- coding: utf-8 -*-

from project_name import *

DEBUG          = True
DAJAXICE_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG


LOGGING = {
    'loggers': {
        '': {
            'handlers': ['mail_admin', 'console'], # can be: null, console, mail_admin
            'level': 'ERROR',
            },
        '%s' % PROJECT_INSTANCE_NAME: {
            'handlers': ['console'], # can be: null, console, mail_admin
            'level': 'WARNING',
            'propagate': True,
            },
    }
}


BASEPATH      = '/www/autoup/%s/'				% PROJECT_INSTANCE_NAME
STATIC_ROOT   = BASEPATH + '../static-roots/%s/' % PROJECT_INSTANCE_NAME
SITE_URL      = 'http://dev.arsh.co/%s/'	% PROJECT_INSTANCE_NAME
LOGIN_URL     = '/accounts/login/'
TEMPLATE_DIRS = (
	'/usr/local/lib/python2.7/dist-packages/django/contrib/admin/templates/',
)


SERVE_STATIC_FILES = True


SECRET_KEY    = 'autoup!' # ATTENTION: DON'T COMMIT THIS LINE


DATABASES = {
#    'default': {
#        'ENGINE':   'django.db.backends.mysql',
#        'NAME':     '%s' % PROJECT_INSTANCE_NAME,
#        'USER':     '%s' % PROJECT_INSTANCE_NAME,
#		'PASSWORD': '?', # ATTENTION: DON'T COMMIT THIS LINE
#        'HOST':     '',
#        'PORT':     '',
#    },
	'default': {
		'ENGINE':   'django.db.backends.sqlite3',
		'NAME':     '%ssrc/%s.sqlite' % (BASEPATH, PROJECT_INSTANCE_NAME),
		'USER':     'root',
		'PASSWORD': '',
		'HOST':     '',
		'PORT':     '',
		}
}

ADMINS = (
#    ('?',                    '?'),
    ('Arsh Server Admin',    'server@arsh.co.ir'),
)
