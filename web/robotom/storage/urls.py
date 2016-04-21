from django.conf.urls import patterns, url
from storage import views

urlpatterns = patterns('',
                       url(r'^$', views.storage_view, name='index'),
                       url(r'^storage_record_(?P<storage_record_id>[a-zA-Z\d\-]+)/$', views.storage_record_view,
                           name='storage_record'),
                       url(r'^frames_downloading_(?P<storage_record_id>[a-zA-Z\d\-]+)/$', views.frames_downloading,
                           name='frames_downloading'),
                       url(r'^delete_experiment_(?P<experiment_id>[a-zA-Z\d\-]+)/$', views.delete_experiment,
                           name='delete_experiment'),
                       url(r'^record_reconstruction_(?P<storage_record_id>[a-zA-Z\d\-]+)/$', views.record_reconstruction,
                           name='record_reconstruction'),
                       url(r'^record_reconstruction_loading_(?P<storage_record_id>[a-zA-Z\d\-]+)/$',
                           views.record_reconstruction_loading,
                           name='record_reconstruction_loading'
                           ),
                       url(r'^record_reconstruction_downloading_(?P<storage_record_id>[a-zA-Z\d\-]+)/$',
                           views.record_reconstruction_downloading,
                           name='record_reconstruction_downloading'
                           )
                       )
