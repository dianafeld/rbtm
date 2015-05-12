from django.conf.urls import patterns, include, url
from storage import views

urlpatterns = patterns('',
                       url(r'^$', views.storage_view, name='index'),
                       url(r'^storage_record(?P<storage_record_id>[a-zA-Z\d\-]+)/$', views.storage_record_view,
                           name='storage_record'),
                       )
