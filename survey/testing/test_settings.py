__author__ = 'simonyu'

from sleepvl.settings import *

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'sleepvl'
}

# Installed the Django test runnere
INSTALLED_APPS += ('django_nose',)

#  Indicate Django to use the Nose test runner.
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# NOSE settings
NOSE_ARGS = [
    '--with-coverage',  # activate coverage report
    '--with-doctest',  # activate doctest: find and run docstests
    '--verbosity=1',  # verbose output
    '--with-xunit',  # enable XUnit plugin
    '--xunit-file= testing/reporter/xunittest.xml',  # the XUnit report file
    '--cover-xml',  # produle XML coverage info
    '--cover-xml-file=testing/reporter/coverage.xml',  # the coverage info file
    '--cover-package=survey',  # Specify the packages to be covered here
]
