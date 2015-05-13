from django.conf.urls import patterns, include, url
from experiment import views

urlpatterns = patterns('',
                       url(r'^$', views.experiment_view, name='index'),
                       url(r'^turn_on/$', views.experiment_start, name='turn_on'),
                       url(r'^turn_off/$', views.experiment_start, name='turn_off'),
                       url(r'^adjustment/$', views.experiment_view_adjustment, name='index_adjustment'),
                       url(r'^adjustment/gate$', views.experiment_start, name='gate'),
                       url(r'^interface/$', views.experiment_view_interface, name='index_interface'),
                       url(r'^start_exp$', views.experiment_start, name='start_experiment'),
                       #url(r'^adjustment/start_experiment/accepted$', views.adjustment_start, name='start_adjustment'),
                       url(r'^interface/send_parameters', views.in_process, name='send_parameters'),
                       url(r'^adjustment/picture$', views.in_process, name='picture')
						)
