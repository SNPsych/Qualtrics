"""
Django settings for sleepvl project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'po&@6kwvfn$cp+jx^1%p18$#v9iip939wkr6lgk=+a@vc79+%6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'survey',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sleepvl.urls'

WSGI_APPLICATION = 'sleepvl.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sleepvl',  # change to correct database name.
        'USER': 'mercdev',  # change to correct user name
        'PASSWORD': 'merc2dev',  # change to correct password
        'HOST': '127.0.0.1',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',  # Set to empty string for default.
    }
}

# Import the local_settings.py to override some of the default settings, like database settings
try:
    from local.local_settings import *
except ImportError:
    logging.warning("No local_settings file found.")

# If it's running testing, it will importing the testing settings,
# The tests settings.py which is under tests directory
import sys

if 'test' in sys.argv:
    from testing.test_settings import *

# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = True


CRONJOBS = [
    ('30 15 * * *', 'survey.cron.survey_cron.survey_rest_call_job', '&> /dev/null')
]

# CRONJOBS = [
#     ('*/3 * * * *', 'survey.cron.survey_cron.survey_rest_call_job', '&> /srv/sleepvl/reports/cron_survey.log')
# ]

# Survey rest api settings
REST_SURVEY_API_URL = 'https://survey.qualtrics.com//WRAPI/ControlPanel/api.php'

REST_API_PARAMS = {
    'API_SELECT': 'ControlPanel',
    'Version': '2.5',
    'Request': 'getLegacyResponseData',
    'User': 'insomnia@monash.edu',
    'Token': 'd6GIsokT7zoPJkfJld4aYNxLEOBsTAZirGzHdRRy',
    'Format': 'CSV',
    'SurveyID': 'SV_cTlmWXeiCQ2PLcF',
    'Labels': '1',
    'ExportTags': '1',
    'ExportQuestionIDs': '1'
}

# Survey temp downloads directory
SURVEY_DOWNLOADS_DIR = os.path.join(BASE_DIR, 'tmp_downloads')
INDEX_HTML_TPL_DIR = os.path.join(BASE_DIR, 'tpl')
SURVEY_OUTPUT_DIR = '/srv/sleepvl/survey'
SURVEY_FILE_PREFIX = 'mon'
SURVEY_REPORT_DIR = '/srv/sleepvl/reports'
SURVEY_LATEST_REPORT_DIR = '/srv/sleepvl/latest_reports'
SURVEY_LATEST_REPORT_INDEX_DIR = '/srv/sleepvl/latest'

RSCRIPTS_COMMAND_PATH = os.path.join(BASE_DIR, 'r_scripts')

# For Linux CentOS 6
R_PATH = '/usr/bin'
R_ENV_PATH = 'PATH="$PATH:/usr/bin"'

# For Max OS
# R_PATH = '/usr/local/bin'
# R_ENV_PATH = 'PATH="$PATH:/usr/local/bin:/Library/TeX/Distributions/.DefaultTeX/Contents/Programs/texbin"'


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'static'))

STATIC_URL = '/static/'

STATIC_PATH = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    STATIC_PATH,
)

# Templates path
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')
TEMPLATE_DIRS = (
    TEMPLATE_PATH,
)
