from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()
from django.core.urlresolvers import reverse

urlpatterns = patterns('',
    url('', include('main.urls', namespace='main')),
    url(r'^experiment/', include('experiment.urls', namespace='experiment')),
    url(r'^storage/', include('storage.urls', namespace='storage')),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
)
