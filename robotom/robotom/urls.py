from django.conf.urls import patterns, include, url
import views
from django.contrib import admin
admin.autodiscover()
from django.core.urlresolvers import reverse

urlpatterns = patterns('',
    url('', include('main.urls', namespace='main')),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
)
