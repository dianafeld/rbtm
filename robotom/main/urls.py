from django.conf.urls import patterns, include, url
from main import views


urlpatterns = patterns('',                       
    url(r'^$', views.index, name='index'),
    url(r'^group1/', views.group1, name='group_1'),
    url(r'^group2/', views.group2, name='group_2'),
    url(r'^group3/', views.group3, name='group_3'),
    url(r'^profile/$', views.profile_view, name='profile_view'),
)
