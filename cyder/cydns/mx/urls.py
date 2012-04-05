from django.conf.urls.defaults import *

from cyder.cydns.mx.views import *

urlpatterns = patterns('',
    url(r'^$', MXListView.as_view() ),
    url(r'create/$', MXCreateView.as_view()),
    url(r'(?P<domain>[\w-]+)/create/$', MXCreateView.as_view()),
    url(r'(?P<pk>[\w-]+)/update/$', MXUpdateView.as_view() ),
    url(r'(?P<pk>[\w-]+)/detail/$', MXDetailView.as_view() ),
    url(r'(?P<pk>[\w-]+)/delete/$', MXDeleteView.as_view() ),

)
