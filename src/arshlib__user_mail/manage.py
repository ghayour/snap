#!/usr/bin/env python
import sys, os
from django.core.management                import execute_manager

directories = os.path.realpath(__file__).split('/')
if len(directories) == 1:
    directories = os.path.realpath(__file__).split('\\')
directories.pop()
directories.pop()
directories.pop()
project_dir = "/".join(directories)
sys.path.append("%s/src" % project_dir)
sys.path.append("%s/lib" % project_dir)

from project_name                            import *

try:
    settings = __import__('%s.settings' % PROJECT_NAME, globals(), locals(), ['*'])
except ImportError:
    sys.stderr.write("ERROR: can't import settings. please contact ARSH admin. thanks")
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)

