from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'reverse_nameserver/$', RevNSListView.as_view()),
    url(r'reverse_nameserver/create/$', RevNSCreateView.as_view()),
    url(r'reverse_nameserver/(?P<pk>[\w-]+)/$', RevNSDetailView.as_view()),
    url(r'reverse_nameserver/(?P<reverse_domain_pk>[\w-]+)/create/$', RevNSCreateView.as_view()),
    url(r'reverse_nameserver/(?P<pk>[\w-]+)/update/$', RevNSUpdateView.as_view()),
    url(r'reverse_nameserver/(?P<pk>[\w-]+)/delete/$', RevNSDeleteView.as_view()),
)
