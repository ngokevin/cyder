from cyder.cydns.soa.models import SOA
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsListView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsUpdateView


class SOAView(object):
    model = SOA
    form_class = SOAForm
    queryset = SOA.objects.all()


class SOADeleteView(SOAView, CydnsDeleteView):
    """ """


class SOADetailView(SOAView, CydnsDetailView):
    """ """
    template_name = 'soa/soa_detail.html'
    context_object_name = 'soa'


class SOACreateView(SOAView, CydnsCreateView):
    """ """


class SOAUpdateView(SOAView, CydnsUpdateView):
    """ """


class SOAListView(SOAView, CydnsListView):
    """ """
    template_name = 'soa/soa_list.html'
