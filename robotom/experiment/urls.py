from django.conf.urls import patterns, include, url
from experiment import views

urlpatterns = patterns('',
                       url(r'^$', views.experiment_view, name='index'),
                       url(r'^on', views.check, name='check'),
                       url(r'^start', views.experiment_start, name='experiment_on'),
                       url(r'^send', views.send_parameters, name='send_parameters'),
                       url(r'^image', views.show_image, name='show_image'),                       
                       
						)
