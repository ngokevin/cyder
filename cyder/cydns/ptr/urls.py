from django.conf.urls.defaults import *

from cyder.cydns.ptr.views import *

urlpatterns = patterns('',
    url(r'^$', PTRListView.as_view() ),
    url(r'create/$', PTRCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', PTRUpdateView.as_view() ),
    url(r'(?P<pk>[\w-]+)/detail/$', PTRDetailView.as_view() ),
    url(r'(?P<pk>[\w-]+)/delete/$', PTRDeleteView.as_view() ),
)
