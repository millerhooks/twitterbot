"""
WSGI config for brandly project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
import site
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "twitterbot.settings")

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/appenv/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/django')
sys.path.append('/home/django/twitterbot')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
application = Sentry(application)
