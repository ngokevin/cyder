from django.conf.urls.defaults import patterns, include, url
from cyder.cydns.soa.views import SOADetailView, SOACreateView, SOAUpdateView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    #########
    # CYDNS #
    #########
    # SOA
    url(r'^cyder/cydns/soa/create$', SOACreateView.as_view() ),
    url(r'^cyder/cydns/soa/(?P<pk>[\w-]+)/update$', SOAUpdateView.as_view() ),
    url(r'^cyder/cydns/soa/(?P<pk>[\w-]+)/detail$', SOADetailView.as_view() ),

    # Domain
    url(r'^cyder/cydns/domain$', 'cyder.cydns.domain.views.domain_list'),
    url(r'^cyder/cydns/domain/create$', 'cyder.cydns.domain.views.domain_create'),
    url(r'^cyder/cydns/domain/(?P<pk>[\w-]+)/update$', 'cyder.cydns.domain.views.domain_update'),

    # Reverse Domain
    url(r'^cyder/cydns/reverse_domain$', 'cyder.cydns.reverse_domain.views.reverse_domain_list'),
    url(r'^cyder/cydns/reverse_domain/create$', 'cyder.cydns.reverse_domain.views.reverse_domain_create'),
    url(r'^cyder/cydns/reverse_domain/(?P<pk>[\w-]+)/update$', 'cyder.cydns.reverse_domain.views.reverse_domain_update'),
    url(r'^cyder/cydns/reverse_domain/bootstrap6$', 'cyder.cydns.reverse_domain.views.bootstrap_ipv6'),
    url(r'^cyder/cydns/reverse_domain/(?P<pk>[\w-]+)/inheirit_soa$', 'cyder.cydns.reverse_domain.views.inheirit_soa'),

    # Address Record
    url(r'^cyder/cydns/address_record/create$', 'cyder.cydns.address_record.views.address_record_create'),
    url(r'^cyder/cydns/address_record/(?P<pk>[\w-]+)/update$', 'cyder.cydns.address_record.views.address_record_update'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
