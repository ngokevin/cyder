from django.conf import settings
from django.conf.urls.defaults import *

from cyder.core.cyuser.views import *

urlpatterns = patterns('',
    url(r'^$', CyuserListView.as_view()),
    url(r'become_user/', 'become_user'),
)
