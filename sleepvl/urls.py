from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       # index page:
                       url(r'^$', 'views.index', name='index'),
                       # django admin
                       url(r'^admin/', include(admin.site.urls)),
                       )
