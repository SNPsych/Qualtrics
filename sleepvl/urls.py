from django.conf.urls import patterns, include, url
from django.contrib import admin
from survey.views import site_admin

urlpatterns = patterns('',
                       # index page:
                       url(r'^$', 'survey.views.index', name='index'),
                       # django admin
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^site-admin', site_admin)
                       )
