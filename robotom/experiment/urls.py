from django.conf.urls import patterns, include, url
from experiment import views

urlpatterns = patterns('',
                       url(r'^$', views.experiment_view, name='index'),
                       )
