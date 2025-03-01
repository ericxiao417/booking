"""
Development settings for the booking project.
"""
from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']  # noqa
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa
INTERNAL_IPS = ['127.0.0.1']
