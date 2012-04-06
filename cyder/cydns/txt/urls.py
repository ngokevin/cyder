from django.conf.urls.defaults import *

from cyder.cydns.txt.views import *

urlpatterns = patterns('',
    url(r'^$', TXTListView.as_view()),
    url(r'create/$', TXTCreateView.as_view()),
    url(r'(?P<domain>[\w-]+)/create/$', TXTCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', TXTUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/detail/$', TXTDetailView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', TXTDeleteView.as_view()),
)
