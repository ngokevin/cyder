from django.conf.urls.defaults import *

from cyder.cybind.views import sample_build
from cyder.cydns.views import Cydns
from cyder.cydns.nameserver.views import *

urlpatterns = patterns('',
    url(r'^$', Cydns.as_view()),

    url(r'build/$', sample_build),

    url(r'reverse_domain/', include('cyder.cydns.reverse_domain.urls')),

    # TODO: separate reverse_ns and ns into separate apps
    url(r'reverse_nameserver/$', RevNSListView.as_view()),
    url(r'reverse_nameserver/create/$', RevNSCreateView.as_view()),
    url(r'reverse_nameserver/(?P<reverse_domain_pk>[\w-]+)/create/$', RevNSCreateView.as_view()),
    url(r'reverse_nameserver/(?P<pk>[\w-]+)/update/$', RevNSUpdateView.as_view()),
    url(r'reverse_nameserver/(?P<pk>[\w-]+)/detail/$', RevNSDetailView.as_view()),
    url(r'reverse_nameserver/(?P<pk>[\w-]+)/delete/$', RevNSDeleteView.as_view()),

    url(r'address_record/', include('cyder.cydns.address_record.urls')),
    url(r'domain/', include('cyder.cydns.domain.urls')),
    url(r'cname/', include('cyder.cydns.cname.urls')),
    url(r'mx/', include('cyder.cydns.mx.urls')),
    url(r'ptr/', include('cyder.cydns.ptr.urls')),
    url(r'soa/', include('cyder.cydns.soa.urls')),
    url(r'srv/', include('cyder.cydns.srv.urls')),
    url(r'txt/', include('cyder.cydns.txt.urls')),

    url(r'nameserver/', include('cyder.cydns.nameserver.urls')),
)
