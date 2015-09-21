# Set up django-crontab

pip install django-crontab

#add it to installed apps in django settings.py:

INSTALLED_APPS = (
    'django_crontab',
    ...
)

#Now create a new method that should be executed by cron every 5 minutes, f.e. in myapp/cron.py:

def my_scheduled_job():
  pass


#define your cron job module and  add this to your settings.py:

CRONJOBS = [
    ('*/5 * * * *', 'myproject.myapp.cron.my_scheduled_job')
]

Please see settings for more details