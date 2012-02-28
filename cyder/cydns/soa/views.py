# Create your views here.
###########
#   SOA   #
###########
from cyder.cydns.soa.models import SOA
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView, CommonDeleteView

class SOAView(object):
    model = SOA
    form_class = SOAForm
    queryset = SOA.objects.all()

class SOADeleteView(SOAView, CommonDeleteView):
    """ """

class SOADetailView(SOAView, CommonDetailView):
    """ """

class SOACreateView(SOAView, CommonCreateView):
    """ """

class SOAUpdateView(SOAView, CommonUpdateView):
    """ """

class SOAListView(SOAView, CommonListView):
    """ """
