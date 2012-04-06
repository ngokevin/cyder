from django.conf.urls.defaults import *

from cyder.cydns.domain.views import *

urlpatterns = patterns('',
    url(r'^$', DomainListView.as_view()),
    url(r'create/$', DomainCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', DomainUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', DomainDeleteView.as_view()),
    url(r'(?P<pk>[\w-]+)/$', DomainDetailView.as_view()),
)
