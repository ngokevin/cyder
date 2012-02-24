# Create your views here.
###########
#   SOA   #
###########
from cyder.cydns.soa.models import SOA
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView

class SOAView(object):
    model = SOA
    form_class = SOAForm
    queryset = SOA.objects.all()

class SOADetailView(SOAView, CommonDetailView):
    pass

class SOACreateView(SOAView, CommonCreateView):
    pass

class SOAUpdateView(SOAView, CommonUpdateView):
    pass

class SOAListView(SOAView, CommonListView):
    pass
