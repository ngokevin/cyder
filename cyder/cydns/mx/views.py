# Create your views here.
from cyder.cydns.mx.models import MX
from cyder.cydns.mx.forms import MXForm
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonDeleteView
from cyder.cydns.common.views import CommonUpdateView, CommonListView

class MXView(object):
    """Group together common attributes."""
    model      = MX
    form_class = MXForm
    queryset   = MX.objects.all()

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
