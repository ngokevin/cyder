# Create your views here.
from cyder.cydns.mx.models import MX
from cyder.cydns.mx.forms import MXForm
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView
############
#    MX    #
############
class MXView(object):
    model      = MX
    form_class = MXForm
    queryset   = MX.objects.all() # Eventually, do a filter here to make user specific views.

class MXDetailView(MXView, CommonDetailView):
    pass

class MXCreateView(MXView, CommonCreateView):
    pass

class MXUpdateView(MXView, CommonUpdateView):
    pass

class MXListView(MXView, CommonListView):
    pass
