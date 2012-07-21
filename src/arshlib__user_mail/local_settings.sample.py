# -*- coding: utf-8 -*-

from project_name import *

DEBUG          = True
DAJAXICE_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG


LOGGING = {
    'loggers': {
        '': {
            'handlers': ['console'], # can be: null, console, mail_admin
            'level': 'WARNING',
            },
        '%s' % PROJECT_INSTANCE_NAME: {
            'handlers': ['console'], # can be: null, console, mail_admin
            'level': 'DEBUG',
            },
        'django.request': {
            'handlers': ['console'], # can be: null, console, mail_admin
            #'filters': ['require_debug_false'], # means when debug set to false do logging
            'level': 'WARNING',
            },
        'django.db.backends': { # For performance reasons, SQL logging is only enabled when settings.DEBUG is set to True
			'handlers': ['console'], # can be: null, console, mail_admin
            'level': 'WARNING',
        },
    }
}


BASEPATH      = '?/%s/'             % PROJECT_INSTANCE_NAME
STATIC_ROOT   = BASEPATH + 'static/'
SITE_URL      = 'http://127.0.0.1:8000/'
LOGIN_URL     = '/accounts/login/'

TEMPLATE_DIRS = ( # in here JUST import django admin templates
	'/usr/local/lib/python2.6/dist-packages/Django-1.3.1-py2.6.egg/django/contrib/admin/templates', # for ubuntu 10.04 users with easy_install
	'/usr/local/lib/python2.7/dist-packages/Django-1.3.1-py2.7.egg/django/contrib/admin/templates', # for other ubuntu users with easy_install
	'/usr/local/lib/python2.6/dist-packages/django/contrib/admin/templates', # for ubuntu 10.04 users
	'/usr/local/lib/python2.7/dist-packages/django/contrib/admin/templates', # for other ubuntu users
	'C:/Python27/Lib/site-packages/django/contrib/admin/templates/', # for windows users
)


SERVE_STATIC_FILES = True


SECRET_KEY    = 'local!'


DATABASES = {
#		'default': {
#			'ENGINE':   'django.db.backends.mysql',
#			'NAME':     '%s' % PROJECT_INSTANCE_NAME,
#			'USER':     'root',
#			'PASSWORD': '',
#			'HOST':     '',
#			'PORT':     '',
#			},
		'default': {
			'ENGINE':   'django.db.backends.sqlite3',
			'NAME':     '%s.sqlite' % PROJECT_INSTANCE_NAME,
			'USER':     'root',
			'PASSWORD': '',
			'HOST':     '',
			'PORT':     '',
			}

		}

ADMINS = ( # for email bugs to you
		#    ('your name',                    'your email'),
		)
