from django.conf.urls import patterns, include, url
from main import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^group1/', views.group1, name='group_1'),
                       url(r'^group2/', views.group2, name='group_2'),
                       url(r'^group3/', views.group3, name='group_3'),

                       url(r'^accounts/profile/$', views.profile_view, name='profile'),
                       url(r'^register/$', views.registration_view, name='register'),
                       url(r'^accounts/done/$', views.done_view, name='done'),
                       url(r'^role_request/$', views.role_request_view, name='role_request'),
                       url(r'^manage_requests/$', views.manage_requests_view, name='manage_requests'),
                       )
