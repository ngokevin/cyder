from cyder.cydns.soa.models import SOA
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.common.views import CommonDeleteView
from cyder.cydns.common.views import CommonListView
from cyder.cydns.common.views import CommonCreateView
from cyder.cydns.common.views import CommonDetailView
from cyder.cydns.common.views import CommonUpdateView


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
