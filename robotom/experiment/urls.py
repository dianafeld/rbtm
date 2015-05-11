from django.conf.urls import patterns, include, url
from experiment import views

urlpatterns = patterns('',
                       url(r'^$', views.experiment_view, name='index'),
                       url(r'^adjustment/$', views.experiment_view_adjustment, name='index_adjustment'),
                       url(r'^interface/$', views.experiment_view_interface, name='index_interface'),
                       url(r'^adjustment/start_experiment$', views.experiment_start, name='start_experiment'),
                       url(r'^interface/send_parameters', views.in_process, name='send_parameters'),
                       url(r'^show_image/image$', views.show_image, name='show_image'),
                       url(r'^show_image/$', views.experiment_view_image, name='image')
						)
