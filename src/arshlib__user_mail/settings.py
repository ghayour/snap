# -*- coding: utf-8 -*-

#noinspection PyBroadException
try:
    from local_settings  import *       #@UnusedWildImport IGNORE:W0614
except:
#noinspection PyBroadException
    try:
        from remote_settings  import *       #@UnusedWildImport IGNORE:W0614
    except:
        from autoup_settings  import *       #@UnusedWildImport IGNORE:W0614

LOGGING.update({
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
            },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            },
        'mail_admin': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            }
    },
    #    'filters': { #not in django till now
    #        'require_debug_false': {
    #            '()': 'django.utils.log.RequireDebugFalse',
    #        }
    #    },
})

MANAGERS = ADMINS

LANGUAGE_CODE = 'fa-IR'
TIME_ZONE = 'Iran'
USE_I18N = True
USE_L10N = True

SEND_BROKEN_LINK_EMAILS = True
EMAIL_SUBJECT_PREFIX = "%s: " % PROJECT_INSTANCE_NAME

SITE_ID = 1

MEDIA_ROOT = BASEPATH + 'media/'
MEDIA_URL = SITE_URL + 'media/'

UPLOAD_URL = BASEPATH + 'media/uploads/'

STATIC_ROOT = BASEPATH + '../static-roots/%s/' % PROJECT_INSTANCE_NAME
STATIC_URL = SITE_URL + 'static/'
ADMIN_STATIC_URL = STATIC_URL + 'admin/'
IMAGES_URL = STATIC_URL + 'images/'
CSS_URL = STATIC_URL + 'css/'
JS_URL = STATIC_URL + 'js/'

STATICFILES_DIRS = (BASEPATH + 'static/',)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

TEMPLATE_DIRS = (
    BASEPATH + 'templates/',
    ) + TEMPLATE_DIRS

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.eggs.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.request",
                               "django.contrib.messages.context_processors.messages"
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

ROOT_URLCONF = '%s.urls' % PROJECT_NAME

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'arsh.tree_model',
    '.sample',
)
