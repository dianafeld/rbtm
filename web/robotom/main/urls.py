from django.conf.urls import patterns, include, url
from django.conf import settings
from main import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^group1/', views.group1, name='group_1'),
                       url(r'^group2/', views.group2, name='group_2'),
                       url(r'^group3/', views.group3, name='group_3'),

                       url(r'^accounts/profile/$', views.profile_view, name='profile'),
                       url(r'^accounts/confirm/(?P<activation_key>[0-9A-Za-z]+)/$', views.confirm_view,
                           name='registration_confirm'),

                       url(r'^accounts/register/$', views.registration_view, name='register'),
                       url(r'^accounts/done/$', views.done_view, name='done'),
                       url(r'^accounts/login/$', views.login_view, name='login'),
                       url(r'^role_request/$', views.role_request_view, name='role_request'),
                       url(r'^manage_requests/$', views.manage_requests_view, name='manage_requests'),
                       )
if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
