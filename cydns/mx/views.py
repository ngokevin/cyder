# Create your views here.
"""
from django.views.generic import DetailView, CreateView, UpdateView

from cyder.cydns.mx.models import MX, MXForm

import pdb

class MXDetailView(DetailView):
    context_object_name = "mx"
    template_name = "mx_detail.html"
    queryset = MX.objects.all()

class MXCreateView(CreateView):
    model = MX
    form_class = MXForm
    template_name = "mx_form.html"
    context_object_name = "mx"
    user = None

    def get_form(self, form_class):
        form = super(MXCreateView, self).get_form( form_class)
        # This is where filtering domain selection should take place.
        # form.fields['domain'].queryset = Domain.objects.filter( name = 'foo.com')
        # This ^ line will change the query set to something controllable
        # find user credentials in self.request
        pdb.set_trace()
        return form

    def post(self, request, *args, **kwargs ):
        try:
            mx = super(MXCreateView, self).post(request, *args, **kwargs)
        except Exception, e:
            messages.error( request, str(e) )
            return super(MXCreateView, self).get(request, *args, **kwargs)
        return mx
    def get(self, request, *args, **kwargs ):
        return super(MXCreateView, self).get(request, *args, **kwargs)

class MXUpdateView(UpdateView):
    template_name = "mx_form.html"
    context_object_name = "mx"
    form_class = MXForm
    queryset = MX.objects.all()

    def post(self, request, *args, **kwargs ):
        try:
            mx = super(MXUpdateView, self).post(request, *args, **kwargs)
        except Exception, e:
            messages.error( request, str(e) )
            request.method = 'GET'
            return super(MXUpdateView, self).get(request, *args, **kwargs)
        return mx
    def get(self, request, *args, **kwargs ):
        return super(MXUpdateView, self).get(request, *args, **kwargs)
"""
