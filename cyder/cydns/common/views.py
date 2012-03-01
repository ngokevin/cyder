from django.views.generic import DetailView, CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.forms import ValidationError
from cyder.settings import CYDNS_BASE_URL
import pdb

class CommonDeleteView(DeleteView):
    context_object_name = "common"
    template_name = "common_delete.html"
    success_url = "/cyder/cydns"
    def get_object(self, queryset=None):
        obj = super(CommonDeleteView, self).get_object()
        # Object permissions here
        return obj

    def delete(self, request, *args, **kwargs):
        # Get the object that we are deleting
        obj = get_object_or_404( self.form_class.Meta.model, pk = kwargs.get('pk', 0))
        try:
            view = super(CommonDeleteView, self).delete(request, *args, **kwargs)
        except ValidationError, e:
            messages.error( request, "Error: %s" % (' '.join(e.messages) ) )
            return redirect( obj )
        messages.success( request, "Deletion Successful" )
        return view

class CommonDetailView(DetailView):
    context_object_name = "common"
    template_name = "common_detail.html"
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['form_title'] = "%s Details" % (self.form_class.Meta.model.__name__)
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
            obj = super(CommonCreateView, self).post(request, *args, **kwargs)
        except ValidationError, e:
            messages.error( request, str(e) )
            request.method = 'GET'
            return super(CommonCreateView, self).get(request, *args, **kwargs)
        return obj
    def get(self, request, *args, **kwargs ):
        return super(CommonCreateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['form_title'] = "Create %s" % (self.form_class.Meta.model.__name__)
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
            obj = super(CommonUpdateView, self).post(request, *args, **kwargs)
        except ValidationError, e:
            messages.error( request, str(e) )
            request.method = 'GET'
            return super(CommonUpdateView, self).get(request, *args, **kwargs)
        return obj
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



"""
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView
class XXXView(object):
    model      = XXX
    form_class = XXXForm
    queryset   = XXX.objects.all()

class XXXDetailView(XXXView, CommonDetailView):
    """ """

class XXXCreateView(XXXView, CommonCreateView):
    """ """

class XXXUpdateView(XXXView, CommonUpdateView):
    """ """

class XXXListView(XXXView, CommonListView):
    """ """
"""
