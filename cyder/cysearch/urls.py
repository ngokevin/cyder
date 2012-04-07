from django.conf.urls.defaults import *
from cyder.cysearch.views import dns_search
from cyder.cysearch.views import dns_results


urlpatterns = patterns('',
    url(r'dns/$', dns_search),
    url(r'dns/results/$', dns_results),
)
