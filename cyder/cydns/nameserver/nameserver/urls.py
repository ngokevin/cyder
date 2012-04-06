from django.conf.urls.defaults import *

from cyder.cydns.nameserver.nameserver.views import *

urlpatterns = patterns('',
    url(r'^$', NSListView.as_view()),
    url(r'create/$', NSCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/$', NSDetailView.as_view()),
    url(r'(?P<domain>[\w-]+)/create/$', NSCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', NSUpdateView.as_view()),
    url(r'(?P<pk>[\w-]+)/delete/$', NSDeleteView.as_view()),
)
