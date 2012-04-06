from django.conf import settings
from django.conf.urls.defaults import *

from cyder.cydns.views import Cydns

urlpatterns = patterns('',
    url(r'^$', Cydns.as_view() ),

    url(r'ctnr/', include('cyder.core.ctnr.urls')),
    url(r'cydns/', include('cyder.cydns.urls')),

    url(r'^login/$', 'django_cas.views.login'),
    url(r'^logout/$', 'django_cas.views.logout'),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
