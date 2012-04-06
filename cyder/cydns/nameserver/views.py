# Create your views here.
from django.forms import ValidationError

from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver, ReverseNameserver
from cyder.cydns.nameserver.forms import NameserverForm, ReverseNameserverForm
from cyder.cydns.common.views import CommonDeleteView
from cyder.cydns.common.views import CommonDetailView
from cyder.cydns.common.views import CommonListView
from cyder.cydns.common.views import CommonCreateView
from cyder.cydns.common.views import CommonUpdateView

import pdb


###### Reverse Nameserver ######
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


###### Nameserver ######
class NSView(object):
    model = Nameserver
    form_class = NameserverForm
    queryset = Nameserver.objects.all()


class NSDeleteView(NSView, CommonDeleteView):
    """ """


class NSDetailView(NSView, CommonDetailView):
    template_name = "ns_detail.html"


class NSListView(NSView, CommonListView):
    """ """


class NSCreateView(NSView, CommonCreateView):
    """ """


class NSUpdateView(NSView, CommonUpdateView):
    """ """
