from cyder.cydns.common.views import CommonDeleteView
from cyder.cydns.common.views import CommonDetailView
from cyder.cydns.common.views import CommonCreateView
from cyder.cydns.common.views import CommonUpdateView
from cyder.cydns.common.views import CommonListView
from cyder.cydns.cname.models import CNAME
from cyder.cydns.cname.forms import CNAMEForm


class CNAMEView(object):
    model = CNAME
    form_class = CNAMEForm
    queryset = CNAME.objects.all()


class CNAMEDeleteView(CNAMEView, CommonDeleteView):
    """ """


class CNAMEDetailView(CNAMEView, CommonDetailView):
    template_name = "cname/detail.html"


class CNAMECreateView(CNAMEView, CommonCreateView):
    """ """


class CNAMEUpdateView(CNAMEView, CommonUpdateView):
    """ """


class CNAMEListView(CNAMEView, CommonListView):
    template_name = "cname/list.html"
