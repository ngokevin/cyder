# Create your views here.
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView
from cyder.cydns.txt.models import TXT
from cyder.cydns.txt.forms import TXTForm

class TXTView(object):
    model      = TXT
    form_class = TXTForm
    queryset   = TXT.objects.all()

class TXTDetailView(TXTView, CommonDetailView):
    """ """

class TXTCreateView(TXTView, CommonCreateView):
    """ """

class TXTUpdateView(TXTView, CommonUpdateView):
    """ """

class TXTListView(TXTView, CommonListView):
    """ """
