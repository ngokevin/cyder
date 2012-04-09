from cyder.cydns.mx.models import MX
from cyder.cydns.mx.forms import MXForm
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsListView
from cyder.cydns.views import CydnsUpdateView


class MXView(object):
    """Group together common attributes."""
    model = MX
    form_class = MXForm
    queryset = MX.objects.all()


class MXDeleteView(MXView, CydnsDeleteView):
    """Delete View"""


class MXDetailView(MXView, CydnsDetailView):
    """Detail View"""
    template_name = 'mx/mx_detail.html'


class MXCreateView(MXView, CydnsCreateView):
    """Create View"""


class MXUpdateView(MXView, CydnsUpdateView):
    """Update View"""


class MXListView(MXView, CydnsListView):
    """List View"""
    template_name = 'mx/mx_list.html'
