from django.conf.urls.defaults import *

from cyder.cydns.soa.views import *

urlpatterns = patterns('',
    url(r'^$', SOAListView.as_view()),
    url(r'create/$', SOACreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/$', SOADetailView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', SOAUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', SOADeleteView.as_view()),
)
