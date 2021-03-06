from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from cyder.cybind.views import sample_build

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {'template': 'cydns/cydns.html'}),

    url(r'build/$', sample_build),

    url(r'address_record/', include('cyder.cydns.address_record.urls')),
    url(r'cname/', include('cyder.cydns.cname.urls')),
    url(r'reverse_domain/', include('cyder.cydns.reverse_domain.urls')),
    url(r'domain/', include('cyder.cydns.domain.urls')),
    url(r'mx/', include('cyder.cydns.mx.urls')),
    url(r'reverse_nameserver/', include('cyder.cydns.nameserver.reverse_nameserver.urls')),
    url(r'nameserver/', include('cyder.cydns.nameserver.nameserver.urls')),
    url(r'ptr/', include('cyder.cydns.ptr.urls')),
    url(r'soa/', include('cyder.cydns.soa.urls')),
    url(r'srv/', include('cyder.cydns.srv.urls')),
    url(r'txt/', include('cyder.cydns.txt.urls')),

)
