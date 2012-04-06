from django.conf.urls.defaults import *

from cyder.cydns.reverse_domain.views import *

urlpatterns = patterns('cyder.cydns.reverse_domain.views',
    url(r'^$', ReverseDomainListView.as_view()),
    url(r'create/$', ReverseDomainCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', ReverseDomainUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/detail/$', ReverseDomainDetailView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', ReverseDomainDeleteView.as_view()),
    url(r'bootstrap6/$', 'bootstrap_ipv6'),
    url(r'(?P<pk>[\w-]+)/inheirit_soa/$', 'inheirit_soa'),
)
