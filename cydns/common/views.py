from cyder.cydns.mx.models import MX, MXForm
from cyder.cydns.soa.models import SOA, SOAForm
from django.views.generic import DetailView, CreateView, UpdateView, ListView
from django.contrib import messages
import pdb

class CommonDetailView(DetailView):
    context_object_name = "common"
    template_name = "common_detail.html"
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['form_title'] = "Update %s" % (self.form_class.Meta.model.__name__)
        if self.extra_context:
            # extra_context takes precidence over original values in context
            context = dict(context.items() + self.extra_context.items())
        return context

class CommonCreateView(CreateView):
    template_name = "common_form.html"
    context_object_name = "common"
    extra_context = None

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

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['form_title'] = "Update %s" % (self.form_class.Meta.model.__name__)
        if self.extra_context:
            # extra_context takes precidence over original values in context
            context = dict(context.items() + self.extra_context.items())
        return context

class CommonUpdateView(UpdateView):
    template_name = "common_form.html"
    context_object_name = "common"
    extra_context = None

    def __init__(self, *args, **kwargs):
        super(UpdateView, self).__init__(*args, **kwargs)

    def get_form(self, form_class):
        form = super(CommonUpdateView, self).get_form( form_class)
        return form

    def post(self, request, *args, **kwargs ):
        try:
            mx = super(CommonUpdateView, self).post(request, *args, **kwargs)
        except Exception, e:
            messages.error( request, str(e) )
            request.method = 'GET'
            return super(CommonUpdateView, self).get(request, *args, **kwargs)
        return mx
    def get(self, request, *args, **kwargs ):
        return super(CommonUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['form_title'] = "Update %s" % (self.form_class.Meta.model.__name__)
        if self.extra_context:
            # extra_context takes precidence over original values in context
            context = dict(context.items() + self.extra_context.items())
        return context

class CommonListView(ListView):
    template_name = "list.html"
    context_object_name = "objects"

############
#    MX    #
############
class MXView(object):
    model      = MX
    form_class = MXForm
    queryset   = MX.objects.all() # Eventually, do a filter here to make user specific views.

class MXDetailView(MXView, CommonDetailView):
    pass

class MXCreateView(MXView, CommonCreateView):
    pass

class MXUpdateView(MXView, CommonUpdateView):
    pass

class MXListView(MXView, CommonListView):
    pass

###########
#   SOA   #
###########

class SOAView(object):
    model = SOA
    form_class = SOAForm
    queryset = SOA.objects.all()

class SOADetailView(SOAView, CommonDetailView):
    pass

class SOACreateView(SOAView, CommonCreateView):
    pass

class SOAUpdateView(SOAView, CommonUpdateView):
    pass

class SOAListView(SOAView, CommonListView):
    pass

"""
class XXXDetailView(CommonDetailView):
    template_name =
    queryset = # Eventually, do a filter here to make user specific views.

class XXXCreateView(CommonCreateView):
    model      =
    form_class =
    form_title =

class XXXUpdateView(CommonUpdateView):
    form_class =
    queryset   =
    form_title =

class XXXListView(CommonListView):
    queryset   =
"""
