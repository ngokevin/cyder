# Create your views here.
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView, CommonDeleteView
from cyder.cydns.cname.models import CNAME
from cyder.cydns.cname.forms import CNAMEForm

class CNAMEView(object):
    model      = CNAME
    form_class = CNAMEForm
    queryset   = CNAME.objects.all()

class CNAMEDeleteView(CNAMEView, CommonDeleteView):
    """ """

class CNAMEDetailView(CNAMEView, CommonDetailView):
    """ """

class CNAMECreateView(CNAMEView, CommonCreateView):
    """ """

class CNAMEUpdateView(CNAMEView, CommonUpdateView):
    """ """

class CNAMEListView(CNAMEView, CommonListView):
    """ """
