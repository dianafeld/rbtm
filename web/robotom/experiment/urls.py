from django.conf.urls import patterns, include, url
from experiment import views

urlpatterns = patterns('',
                       url(r'^$', views.experiment_view, name='index'),
                       url(r'^adjustment/$', views.experiment_adjustment, name='index_adjustment'),
                       url(r'^interface/$', views.experiment_interface, name='index_interface'),
                       url(r'^tomograph/(?P<tomo_num>\d+)/set_voltage$', views.set_voltage,
                           name='set_voltage'),
                       url(r'^tomograph/(?P<tomo_num>\d+)/set_current$', views.set_current,
                           name='set_current'),
                       url(r'^tomograph/(?P<tomo_num>\d+)/set_horiz_shift$', views.set_horiz_shift,
                           name='set_horiz_shift'),
                       url(r'^tomograph/(?P<tomo_num>\d+)/set_vert_shift$', views.set_vert_shift,
                           name='set_vert_shift'),
                       url(r'^tomograph/(?P<tomo_num>\d+)/set_shutter$', views.set_shutter,
                           name='set_shutter'),
                       url(r'^tomograph/(?P<tomo_num>\d+)/set_angle$', views.set_angle,
                           name='set_angle'),
                       )
