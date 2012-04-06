from django.conf.urls.defaults import *

from cyder.cydns.nameserver.reverse_nameserver.views import *

urlpatterns = patterns('',
    url(r'^$', RevNSListView.as_view()),
    url(r'create/$', RevNSCreateView.as_view()),
    url(r'(?P<reverse_domain_pk>[\w-]+)/create/$', RevNSCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', RevNSUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', RevNSDeleteView.as_view()),
    url(r'(?P<pk>[\w-]+)/$', RevNSDetailView.as_view()),
)
