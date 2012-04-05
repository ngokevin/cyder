from django.conf.urls.defaults import *

from cyder.cydns.cname.views import *

urlpatterns = patterns('',
    url(r'^$', CNAMEListView.as_view()),
    url(r'create/$', CNAMECreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/$', CNAMEDetailView.as_view()),
    url(r'(?P<domain>[\w-]+)/create/$', CNAMECreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', CNAMEUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', CNAMEDeleteView.as_view()),
)
