from django.conf.urls.defaults import *

from cyder.cydns.srv.views import *

urlpatterns = patterns('',
    url(r'^$', SRVListView.as_view()),
    url(r'(?P<domain>[\w-]+)/create/$', SRVCreateView.as_view()),
    url(r'create/$', SRVCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', SRVUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', SRVDeleteView.as_view()),
    url(r'(?P<pk>[\w-]+)/$', SRVDetailView.as_view()),
)
