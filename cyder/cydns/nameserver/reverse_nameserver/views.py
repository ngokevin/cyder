from cyder.cydns.nameserver.reverse_nameserver.forms import ReverseNameserverForm
from cyder.cydns.nameserver.reverse_nameserver.models import ReverseNameserver
from cyder.cydns.nameserver.views import *

class RevNSView(object):
    model = ReverseNameserver
    form_class = ReverseNameserverForm
    queryset = ReverseNameserver.objects.all()


class RevNSDeleteView(RevNSView, CommonDeleteView):
    """ """


class RevNSDetailView(RevNSView, CommonDetailView):
    """ """


class RevNSListView(RevNSView, CommonListView):
    """ """


class RevNSCreateView(RevNSView, CommonCreateView):
    """ """


class RevNSUpdateView(RevNSView, CommonUpdateView):
    """ """
