#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('', url(r'^show/', include('showControler.urls',
                       namespace='showControler')), url(r'^admin/',
                       include(admin.site.urls)))  # Examples:
                                                   # url(r'^$', 'webServer.views.home', name='home'),
                                                   # url(r'^blog/', include('blog.urls')),
