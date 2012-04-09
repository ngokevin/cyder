from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.soa.models import SOA
from cyder.cydns.utils import tablefy
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsListView
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

    def get_context_data(self, **kwargs):
        context = super(SOADetailView, self).get_context_data(**kwargs)
        soa = kwargs.get('object', False)
        if not soa:
            return soa

        dom_objects = soa.domain_set.all()
        dom_headers, dom_matrix, dom_urls = tablefy(dom_objects)

        rdom_objects = soa.reversedomain_set.all()
        rdom_headers, rdom_matrix, rdom_urls = tablefy(rdom_objects)

        context = dict({
            "dom_headers": dom_headers,
            "dom_matrix": dom_matrix,
            "dom_urls": dom_urls,

            "rdom_headers": rdom_headers,
            "rdom_matrix": rdom_matrix,
            "rdom_urls": rdom_urls,
        }.items() + context.items())

        return context


class SOACreateView(SOAView, CydnsCreateView):
    """ """


class SOAUpdateView(SOAView, CydnsUpdateView):
    """ """


class SOAListView(SOAView, CydnsListView):
    """ """
    template_name = 'soa/soa_list.html'
