# Create your views here.
# Create your views here.
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView
from cyder.cydns.ptr.models import PTR
from cyder.cydns.ptr.forms import PTRForm

class PTRView(object):
    model      = PTR
    form_class = PTRForm
    queryset   = PTR.objects.all()

class PTRDetailView(PTRView, CommonDetailView):
    """ """

class PTRCreateView(PTRView, CommonCreateView):
    """ """

class PTRUpdateView(PTRView, CommonUpdateView):
    """ """

class PTRListView(PTRView, CommonListView):
    """ """
