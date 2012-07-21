import os
import sys
import django.core.handlers.wsgi

directories = os.path.realpath(__file__).split('/')
if len(directories) == 1:
    directories = os.path.realpath(__file__).split('\\')
directories.pop()
mydir = "/".join(directories)
sys.path.append("%s/src" % mydir)
sys.path.append("%s/lib" % mydir)

from project_name                           import *

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % PROJECT_NAME
application = django.core.handlers.wsgi.WSGIHandler()

