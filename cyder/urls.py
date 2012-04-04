from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from cyder.cydns.views import Cydns
from cyder.cydns.soa.views import SOADetailView, SOACreateView, SOAUpdateView, SOAListView, SOADeleteView
from cyder.cydns.mx.views import MXDetailView, MXCreateView, MXUpdateView, MXListView, MXDeleteView
from cyder.cydns.srv.views import SRVDetailView, SRVCreateView, SRVUpdateView, SRVListView, SRVDeleteView
from cyder.cydns.txt.views import TXTDetailView, TXTCreateView, TXTUpdateView, TXTListView, TXTDeleteView
from cyder.cydns.cname.views import CNAMEDetailView, CNAMECreateView, CNAMEUpdateView
from cyder.cydns.cname.views import CNAMEListView, CNAMEDeleteView
from cyder.cydns.ptr.views import PTRDetailView, PTRCreateView, PTRUpdateView, PTRListView, PTRDeleteView
from cyder.cydns.nameserver.views import NSDetailView, NSCreateView, NSUpdateView, NSListView, NSDeleteView
from cyder.cydns.nameserver.views import RevNSUpdateView, RevNSListView, RevNSDeleteView
from cyder.cydns.nameserver.views import RevNSDetailView, RevNSCreateView

from cyder.cydns.domain.views import DomainDetailView, DomainListView, DomainCreateView
from cyder.cydns.domain.views import DomainUpdateView, DomainDeleteView
from cyder.cydns.reverse_domain.views import ReverseDomainDetailView, ReverseDomainListView
from cyder.cydns.reverse_domain.views import ReverseDomainUpdateView, ReverseDomainCreateView
from cyder.cydns.reverse_domain.views import ReverseDomainDeleteView
from cyder.cydns.address_record.views import AddressRecordDetailView, AddressRecordCreateView
from cyder.cydns.address_record.views import AddressRecordUpdateView, AddressRecordDeleteView

from cyder.cybind.views import sample_build


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', Cydns.as_view() ),
    url(r'cydns$', Cydns.as_view() ),
    url(r'cydns/build$', sample_build ),
    # CAS
    url(r'^login$', 'django_cas.views.login'),
    url(r'^logout$', 'django_cas.views.logout'),

    #########
    # CYDNS #
    #########
    # NS
    url(r'cydns/nameserver$', NSListView.as_view() ),
    url(r'cydns/nameserver/create$', NSCreateView.as_view()),
    # CAS
    url(r'^login$', 'django_cas.views.login'),
    url(r'^logout$', 'django_cas.views.logout'),

    #########
    # CYDNS #
    #########
    # NS
    url(r'cydns/nameserver$', NSListView.as_view() ),
    url(r'cydns/nameserver/create$', NSCreateView.as_view()),
    url(r'cydns/nameserver/(?P<domain>[\w-]+)/create$', NSCreateView.as_view()),
    url(r'cydns/nameserver/(?P<pk>[\w-]+)/update$', NSUpdateView.as_view() ),
    url(r'cydns/nameserver/(?P<pk>[\w-]+)/detail$', NSDetailView.as_view() ),
    url(r'cydns/nameserver/(?P<pk>[\w-]+)/delete$', NSDeleteView.as_view() ),

    # Reverse NS
    url(r'cydns/reverse_nameserver$', RevNSListView.as_view() ),
    url(r'cydns/reverse_nameserver/create$', RevNSCreateView.as_view()),
    url(r'cydns/reverse_nameserver/(?P<reverse_domain_pk>[\w-]+)/create$', RevNSCreateView.as_view()),
    url(r'cydns/reverse_nameserver/(?P<pk>[\w-]+)/update$', RevNSUpdateView.as_view() ),
    url(r'cydns/reverse_nameserver/(?P<pk>[\w-]+)/detail$', RevNSDetailView.as_view() ),
    url(r'cydns/reverse_nameserver/(?P<pk>[\w-]+)/delete$', RevNSDeleteView.as_view() ),

    # SRV
    url(r'cydns/srv$', SRVListView.as_view() ),
    url(r'cydns/srv/create$', SRVCreateView.as_view()),
    url(r'cydns/srv/(?P<domain>[\w-]+)/create$', SRVCreateView.as_view()),
    url(r'cydns/srv/(?P<pk>[\w-]+)/update$', SRVUpdateView.as_view() ),
    url(r'cydns/srv/(?P<pk>[\w-]+)/detail$', SRVDetailView.as_view() ),
    url(r'cydns/srv/(?P<pk>[\w-]+)/delete$', SRVDeleteView.as_view() ),

    # TXT
    url(r'cydns/txt$', TXTListView.as_view() ),
    url(r'cydns/txt/create$', TXTCreateView.as_view()),
    url(r'cydns/txt/(?P<domain>[\w-]+)/create$', TXTCreateView.as_view()),
    url(r'cydns/txt/(?P<pk>[\w-]+)/update$', TXTUpdateView.as_view() ),
    url(r'cydns/txt/(?P<pk>[\w-]+)/detail$', TXTDetailView.as_view() ),
    url(r'cydns/txt/(?P<pk>[\w-]+)/delete$', TXTDeleteView.as_view() ),

    # CNAME
    url(r'cydns/cname$', CNAMEListView.as_view() ),
    url(r'cydns/cname/create$', CNAMECreateView.as_view()),
    url(r'cydns/cname/(?P<domain>[\w-]+)/create$', CNAMECreateView.as_view()),
    url(r'cydns/cname/(?P<pk>[\w-]+)/update$', CNAMEUpdateView.as_view() ),
    url(r'cydns/cname/(?P<pk>[\w-]+)/detail$', CNAMEDetailView.as_view() ),
    url(r'cydns/cname/(?P<pk>[\w-]+)/delete$', CNAMEDeleteView.as_view() ),

    # PTR
    url(r'cydns/ptr$', PTRListView.as_view() ),
    url(r'cydns/ptr/create$', PTRCreateView.as_view()),
    url(r'cydns/ptr/(?P<pk>[\w-]+)/update$', PTRUpdateView.as_view() ),
    url(r'cydns/ptr/(?P<pk>[\w-]+)/detail$', PTRDetailView.as_view() ),
    url(r'cydns/ptr/(?P<pk>[\w-]+)/delete$', PTRDeleteView.as_view() ),

    # MX
    url(r'cydns/mx$', MXListView.as_view() ),
    url(r'cydns/mx/create$', MXCreateView.as_view()),
    url(r'cydns/mx/(?P<domain>[\w-]+)/create$', MXCreateView.as_view()),
    url(r'cydns/mx/(?P<pk>[\w-]+)/update$', MXUpdateView.as_view() ),
    url(r'cydns/mx/(?P<pk>[\w-]+)/detail$', MXDetailView.as_view() ),
    url(r'cydns/mx/(?P<pk>[\w-]+)/delete$', MXDeleteView.as_view() ),

    # SOA
    url(r'cydns/soa$', SOAListView.as_view() ),
    url(r'cydns/soa/create$', SOACreateView.as_view() ),
    url(r'cydns/soa/(?P<pk>[\w-]+)/update$', SOAUpdateView.as_view() ),
    url(r'cydns/soa/(?P<pk>[\w-]+)/detail$', SOADetailView.as_view() ),
    url(r'cydns/soa/(?P<pk>[\w-]+)/delete$', SOADeleteView.as_view() ),

    # Domain
    url(r'cydns/domain$', DomainListView.as_view()),
    url(r'cydns/domain/create$', DomainCreateView.as_view()),
    url(r'cydns/domain/(?P<pk>[\w-]+)/update$', DomainUpdateView.as_view()),
    url(r'cydns/domain/(?P<pk>[\w-]+)/detail$', DomainDetailView.as_view()),
    url(r'cydns/domain/(?P<pk>[\w-]+)/delete$', DomainDeleteView.as_view()),

    # Reverse Domain
    url(r'cydns/reverse_domain$', ReverseDomainListView.as_view()),
    url(r'cydns/reverse_domain/create$', ReverseDomainCreateView.as_view()),
    url(r'cydns/reverse_domain/(?P<pk>[\w-]+)/update$', ReverseDomainUpdateView.as_view()),
    url(r'cydns/reverse_domain/(?P<pk>[\w-]+)/detail$', ReverseDomainDetailView.as_view()),
    url(r'cydns/reverse_domain/(?P<pk>[\w-]+)/delete$', ReverseDomainDeleteView.as_view()),
    url(r'cydns/reverse_domain/bootstrap6$', 'cyder.cydns.reverse_domain.views.bootstrap_ipv6'),
    url(r'cydns/reverse_domain/(?P<pk>[\w-]+)/inheirit_soa$', 'cyder.cydns.reverse_domain.views.inheirit_soa'),

    # Address Record
    url(r'cydns/address_record/create$', AddressRecordCreateView.as_view() ),
    url(r'cydns/address_record/(?P<domain>[\w-]+)/create$', AddressRecordCreateView.as_view() ),
    url(r'cydns/address_record/(?P<pk>[\w-]+)/update$', AddressRecordUpdateView.as_view() ),
    url(r'cydns/address_record/(?P<pk>[\w-]+)/detail$', AddressRecordDetailView.as_view() ),
    url(r'cydns/address_record/(?P<pk>[\w-]+)/delete$', AddressRecordDeleteView.as_view() ),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
