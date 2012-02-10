from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    #########
    # CYDNS #
    #########
    # Domain
    url(r'^cyder/cydns/domain$', 'cyder.cydns.domain.views.domain_list'),
    url(r'^cyder/cydns/domain/create$', 'cyder.cydns.domain.views.domain_create'),
    url(r'^cyder/cydns/domain/(?P<pk>[\w-]+)/update$', 'cyder.cydns.domain.views.domain_update'),

    # Reverse Domain
    url(r'^cyder/cydns/reverse_domain$', 'cyder.cydns.reverse_domain.views.reverse_domain_list'),
    url(r'^cyder/cydns/reverse_domain/create$', 'cyder.cydns.reverse_domain.views.reverse_domain_create'),
    url(r'^cyder/cydns/reverse_domain/(?P<pk>[\w-]+)/update$', 'cyder.cydns.reverse_domain.views.reverse_domain_update'),
    url(r'^cyder/cydns/reverse_domain/bootstrap6$', 'cyder.cydns.reverse_domain.views.bootstrap_ipv6'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
