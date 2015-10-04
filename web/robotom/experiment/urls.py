from django.conf.urls import patterns, include, url
from experiment import views

urlpatterns = patterns('',
                       url(r'^$', views.experiment_view, name='index'),
                       url(r'^adjustment/$', views.experiment_adjustment, name='index_adjustment'),
                       url(r'^interface/$', views.experiment_interface, name='index_interface'),
                       )
