from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'robotom.views.index', name='index'),
    url(r'^group1/', 'robotom.views.group1', name='group_1'),
    url(r'^group2/', 'robotom.views.group2', name='group_2'),
    url(r'^group3/', 'robotom.views.group3', name='group_3'),
    url(r'^admin/', include(admin.site.urls)),
)
