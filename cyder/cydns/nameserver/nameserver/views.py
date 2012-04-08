from cyder.cydns.nameserver.nameserver.forms import NameserverForm
from cyder.cydns.nameserver.nameserver.models import Nameserver
from cyder.cydns.nameserver.views import *


class NSView(object):
    model = Nameserver
    form_class = NameserverForm
    queryset = Nameserver.objects.all()


class NSDeleteView(NSView, CommonDeleteView):
    """ """


class NSDetailView(NSView, CommonDetailView):
    template_name = "nameserver/nameserver_detail.html"


class NSListView(NSView, CommonListView):
    """ """
    template_name = "nameserver/nameserver_list.html"


class NSCreateView(NSView, CommonCreateView):
    """ """


class NSUpdateView(NSView, CommonUpdateView):
    """ """
