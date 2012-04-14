from cyder.cydns.nameserver.reverse_nameserver.forms import ReverseNameserverForm
from cyder.cydns.nameserver.reverse_nameserver.models import ReverseNameserver
from cyder.cydns.nameserver.views import *

class RevNSView(object):
    model = ReverseNameserver
    form_class = ReverseNameserverForm
    queryset = ReverseNameserver.objects.all()


class RevNSDeleteView(RevNSView, CydnsDeleteView):
    """ """


class RevNSDetailView(RevNSView, CydnsDetailView):
    """ """
    template_name = "reverse_nameserver/reverse_nameserver_detail.html"


class RevNSListView(RevNSView, CydnsListView):
    """ """
    template_name = "reverse_nameserver/reverse_nameserver_list.html"


class RevNSCreateView(RevNSView, CydnsCreateView):
    """ """


class RevNSUpdateView(RevNSView, CydnsUpdateView):
    """ """
