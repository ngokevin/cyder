from cyder.cydns.nameserver.nameserver.forms import NameserverForm
from cyder.cydns.nameserver.nameserver.models import Nameserver
from cyder.cydns.nameserver.views import *


class NSView(object):
    model = Nameserver
    form_class = NameserverForm
    queryset = Nameserver.objects.all()


class NSDeleteView(NSView, CydnsDeleteView):
    """ """


class NSDetailView(NSView, CydnsDetailView):
    template_name = "nameserver/nameserver_detail.html"


class NSListView(NSView, CydnsListView):
    """ """
    template_name = "nameserver/nameserver_list.html"


class NSCreateView(NSView, CydnsCreateView):
    """ """


class NSUpdateView(NSView, CydnsUpdateView):
    """ """
