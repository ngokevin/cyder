from django.conf.urls.defaults import *

urlpatterns = patterns('cyder.core.ctnr.views',
    url(r'(?P<pk>[\w-]+)?/?change/$', 'change_ctnr'),
)
