from cyder.cydns.mx.models import MX
from cyder.cydns.mx.forms import MXForm
from cyder.cydns.common.views import CommonDeleteView
from cyder.cydns.common.views import CommonDetailView
from cyder.cydns.common.views import CommonCreateView
from cyder.cydns.common.views import CommonListView
from cyder.cydns.common.views import CommonUpdateView


class MXView(object):
    """Group together common attributes."""
    model = MX
    form_class = MXForm
    queryset = MX.objects.all()


class MXDeleteView(MXView, CommonDeleteView):
    """Delete View"""


class MXDetailView(MXView, CommonDetailView):
    """Detail View"""


class MXCreateView(MXView, CommonCreateView):
    """Create View"""


class MXUpdateView(MXView, CommonUpdateView):
    """Update View"""


class MXListView(MXView, CommonListView):
    """List View"""
    template_name = 'mx/list.html'
