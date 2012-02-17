from cyder.cydns.mx.models import MX, MXForm
from cyder.cydns.soa.models import SOA, SOAForm
from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib import messages
import pdb

class CommonDetailView(DetailView):
    context_object_name = "common"

class CommonCreateView(CreateView):
    template_name = "common_form.html"
    context_object_name = "common"

    def get_form(self, form_class):
        form = super(CommonCreateView, self).get_form( form_class)
        # This is where filtering domain selection should take place.
        # form.fields['domain'].queryset = Domain.objects.filter( name = 'foo.com')
        # This ^ line will change the query set to something controllable
        # find user credentials in self.request
        return form

    def post(self, request, *args, **kwargs ):
        try:
            mx = super(CommonCreateView, self).post(request, *args, **kwargs)
        except Exception, e:
            messages.error( request, str(e) )
            request.method = 'GET'
            return super(CommonCreateView, self).get(request, *args, **kwargs)
        return mx
    def get(self, request, *args, **kwargs ):
        return super(CommonCreateView, self).get(request, *args, **kwargs)

class CommonUpdateView(UpdateView):
    template_name = "common_form.html"
    context_object_name = "common"

    def post(self, request, *args, **kwargs ):
        try:
            mx = super(CommonUpdateView, self).post(request, *args, **kwargs)
        except Exception, e:
            messages.error( request, str(e) )
            request.method = 'GET'
            return super(CommonUpdateView, self).get(request, *args, **kwargs)
        pdb.set_trace()
        return mx
    def get(self, request, *args, **kwargs ):
        return super(CommonUpdateView, self).get(request, *args, **kwargs)

class MXDetailView(CommonDetailView):
    template_name = "mx_detail.html"
    queryset = MX.objects.all() # Eventually, do a filter here to make user specific views.

class MXCreateView(CommonCreateView):
    model      = MX
    form_class = MXForm

class MXUpdateView(CommonUpdateView):
    form_class = MXForm
    queryset   = MX.objects.all()

class SOADetailView(CommonDetailView):
    template_name = "soa_detail.html"
    queryset = SOA.objects.all()

class SOACreateView(CommonCreateView):
    model = SOA
    form_class = SOAForm

class SOAUpdateView(CommonUpdateView):
    form_class = SOAForm
    queryset = SOA.objects.all()

"""
class XXXDetailView(CommonDetailView):
    template_name =
    queryset = # Eventually, do a filter here to make user specific views.

class XXXCreateView(CommonCreateView):
    model      =
    form_class =

class XXXUpdateView(CommonUpdateView):
    form_class =
    queryset   =
"""
