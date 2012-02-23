from django.conf.urls.defaults import patterns, include, url
from cyder.cydns.common.views import SOADetailView, SOACreateView, SOAUpdateView, SOAListView
from cyder.cydns.common.views import MXDetailView, MXCreateView, MXUpdateView, MXListView
from cyder.cydns.domain.views import DomainDetailView, DomainListView, DomainCreateView
from cyder.cydns.domain.views import DomainUpdateView
from cyder.cydns.reverse_domain.views import ReverseDomainDetailView, ReverseDomainListView
from cyder.cydns.reverse_domain.views import ReverseDomainUpdateView, ReverseDomainCreateView
from cyder.cydns.nameserver.views import NSDetailView, NSCreateView, NSUpdateView, NSListView
from cyder.cydns.address_record.views import AddressRecordDetailView, AddressRecordCreateView
from cyder.cydns.address_record.views import AddressRecordUpdateView


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    #########
    # CYDNS #
    #########
    # NS
    url(r'^cyder/cydns/nameserver$', NSListView.as_view() ),
    url(r'^cyder/cydns/nameserver/create$', NSCreateView.as_view()),
    url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/update$', NSUpdateView.as_view() ),
    url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/detail$', NSDetailView.as_view() ),

    # MX
    url(r'^cyder/cydns/mx$', MXListView.as_view() ),
    url(r'^cyder/cydns/mx/create$', MXCreateView.as_view()),
    url(r'^cyder/cydns/mx/(?P<pk>[\w-]+)/update$', MXUpdateView.as_view() ),
    url(r'^cyder/cydns/mx/(?P<pk>[\w-]+)/detail$', MXDetailView.as_view() ),

    # SOA
    url(r'^cyder/cydns/soa$', SOAListView.as_view() ),
    url(r'^cyder/cydns/soa/create$', SOACreateView.as_view() ),
    url(r'^cyder/cydns/soa/(?P<pk>[\w-]+)/update$', SOAUpdateView.as_view() ),
    url(r'^cyder/cydns/soa/(?P<pk>[\w-]+)/detail$', SOADetailView.as_view() ),

    # Domain
    url(r'^cyder/cydns/domain$', DomainListView.as_view()),
    url(r'^cyder/cydns/domain/create$', DomainCreateView.as_view()),
    url(r'^cyder/cydns/domain/(?P<pk>[\w-]+)/update$', DomainUpdateView.as_view()),
    url(r'^cyder/cydns/domain/(?P<pk>[\w-]+)/detail$', DomainDetailView.as_view()),

    # Reverse Domain
    url(r'^cyder/cydns/reverse_domain$', ReverseDomainListView.as_view()),
    url(r'^cyder/cydns/reverse_domain/create$', ReverseDomainCreateView.as_view()),
    url(r'^cyder/cydns/reverse_domain/(?P<pk>[\w-]+)/update$', ReverseDomainUpdateView.as_view()),
    url(r'^cyder/cydns/reverse_domain/(?P<pk>[\w-]+)/detail$', ReverseDomainDetailView.as_view()),
    url(r'^cyder/cydns/reverse_domain/bootstrap6$', 'cyder.cydns.reverse_domain.views.bootstrap_ipv6'),
    url(r'^cyder/cydns/reverse_domain/(?P<pk>[\w-]+)/inheirit_soa$', 'cyder.cydns.reverse_domain.views.inheirit_soa'),

    # Address Record
    url(r'^cyder/cydns/address_record/create$', AddressRecordCreateView.as_view() ),
    url(r'^cyder/cydns/address_record/(?P<pk>[\w-]+)/update$', AddressRecordUpdateView.as_view() ),
    url(r'^cyder/cydns/address_record/(?P<pk>[\w-]+)/detail$', AddressRecordDetailView.as_view() ),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
