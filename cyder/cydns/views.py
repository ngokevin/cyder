from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import ListView

from cyder.cydns.domain.models import Domain
from cyder.cydns.utils import slim_form


class CydnsDeleteView(DeleteView):
    template_name = "cydns/cydns_confirm_delete.html"
    success_url = "/cydns"

    def get_object(self, queryset=None):
        obj = super(CydnsDeleteView, self).get_object()
        return obj

    def delete(self, request, *args, **kwargs):
        # Get the object that we are deleting
        obj = get_object_or_404(self.form_class.Meta.model,
                                pk=kwargs.get('pk', 0))
        try:
            view = super(CydnsDeleteView, self).delete(request,
                                                        *args, **kwargs)
        except ValidationError, e:
            messages.error(request, "Error: {0}".format(' '.join(e.messages)))
            return redirect(obj)
        messages.success(request, "Deletion Successful")
        return view


class CydnsDetailView(DetailView):
    template_name = "cydns/cydns_detail.html"
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['form_title'] = "{0} Details".format(self.form_class.Meta.
                                                     model.__name__)
        if self.extra_context:
            # extra_context takes precidence over original values in context
            context = dict(context.items() + self.extra_context.items())
        return context


class CydnsCreateView(CreateView):
    template_name = "cydns/cydns_form.html"
    extra_context = None

    def get_form(self, form_class):
        form = super(CydnsCreateView, self).get_form(form_class)
        domain_pk = self.kwargs.get('domain', False)
        # The use of slim_form makes my eyes bleed and stomach churn.
        if domain_pk:
            form = slim_form(domain_pk=domain_pk, form=form)

        reverse_domain_pk = self.kwargs.get('reverse_domain', False)
        if reverse_domain_pk:
            slim_form(reverse_domain_pk=reverse_domain_pk, form=form)

        # This is where filtering domain selection should take place.
        # form.fields['domain'].queryset = Domain.objects.filter(name =
        # 'foo.com') This ^ line will change the query set to something
        # controllable find user credentials in self.request
        return form

    def post(self, request, *args, **kwargs):
        try:
            obj = super(CydnsCreateView, self).post(request, *args, **kwargs)
        except ValidationError, e:
            messages.error(request, str(e))
            request.method = 'GET'
            return super(CydnsCreateView, self).get(request, *args, **kwargs)
        return obj

    def get(self, request, *args, **kwargs):
        return super(CydnsCreateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['form_title'] = "Create {0}".format(self.form_class.Meta.
                                                    model.__name__)
        if self.extra_context:
            # extra_context takes precidence over original values in context
            context = dict(context.items() + self.extra_context.items())
        return context


class CydnsUpdateView(UpdateView):
    template_name = "cydns/cydns_form.html"
    extra_context = None

    def __init__(self, *args, **kwargs):
        super(UpdateView, self).__init__(*args, **kwargs)

    def get_form(self, form_class):
        form = super(CydnsUpdateView, self).get_form(form_class)
        return form

    def post(self, request, *args, **kwargs):
        try:
            obj = super(CydnsUpdateView, self).post(request, *args, **kwargs)
        except ValidationError, e:
            messages.error(request, str(e))
            request.method = 'GET'
            return super(CydnsUpdateView, self).get(request, *args, **kwargs)
        return obj

    def get(self, request, *args, **kwargs):
        return super(CydnsUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['form_title'] = "Update {0}".format(self.form_class.Meta.
                                                    model.__name__)
        if self.extra_context:
            # extra_context takes precidence over original values in context
            context = dict(context.items() + self.extra_context.items())
        return context


class CydnsListView(ListView):
    template_name = "cydns/cydns_list.html"
    paginate_by = 30


class Cydns(DetailView): #TODO we need a more appropriate Generic CBV

    def get(self, request, *args, **kwargs):
        return render(request, "cydns/cydns.html")
