# Create your views here.
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView, CommonDeleteView
from cyder.cydns.srv.models import SRV
from cyder.cydns.srv.forms import SRVForm
class SRVView(object):
    model      = SRV
    form_class = SRVForm
    queryset   = SRV.objects.all()

class SRVDeleteView(SRVView, CommonDeleteView):
    """SRV Delete View"""
class SRVDetailView(SRVView, CommonDetailView):
    """SRV Detail View"""

class SRVCreateView(SRVView, CommonCreateView):
    """SRV Create View"""

class SRVUpdateView(SRVView, CommonUpdateView):
    """SRV Update View"""

class SRVListView(SRVView, CommonListView):
    """SRV List View"""
