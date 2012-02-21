# Create your views here.
from cyder.cydns.nameserver.models import Nameserver, NameserverForm, _needs_glue
from cyder.cydns.common.views import CommonDetailView, CommonListView
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView, UpdateView, ListView
from django.contrib import messages
from django.forms import ValidationError
import pdb

class NSView(object):
    model      = Nameserver
    form_class = NameserverForm
    queryset   = Nameserver.objects.all() # Eventually, do a filter here to make user specific views.

class NSDetailView(NSView, CommonDetailView):
    template_name = "ns_detail.html"
    pass

class NSListView(NSView, CommonListView):
    pass

class NSCreateView(CreateView):
    template_name = "ns_form.html"
    model      = Nameserver
    form_class = NameserverForm

    def get_form(self, form_class):
        form = super(NSCreateView, self).get_form( form_class)
        # This is where filtering domain selection should take place.
        # form.fields['domain'].queryset = Domain.objects.filter( name = 'foo.com')
        # This ^ line will change the query set to something controllable
        # find user credentials in self.request
        return form

    # Handle this post manually.
    def post(self, request, *args, **kwargs ):
        server = request.POST.get('server', False)
        domain_pk = request.POST.get('domain', False)
        try:
            domain = Domain.objects.get( pk = int(domain_pk) )
        except ValueError, e:
            messages.error( request, "Something went very wrong. domain was not type int." )
            return self.get(self, request, *args, **kwargs)

        if not server:
            messages.error( request, "NS servers must have a server field." )
            return self.get(self, request, *args, **kwargs)

        if not domain:
            messages.error( request, "Please select a domain for this NS to belong to." )
            return self.get(self, request, *args, **kwargs)

        ns = Nameserver( domain = domain, server = server )

        # If ns needs a glue record, find it. It we can't find it return and error.
        if _needs_glue( ns ):
            glue_label = server.split('.')[0] # foo.com -> foo
            # This will cause a problem if there is more than one dns name here.
            glue = AddressRecord.objects.filter( label = glue_label, domain = domain )
            if not glue:
                form = NameserverForm( request.POST )
                return render( request, "ns_form.html", {'form': form } )
            else:
                ns.glue = glue[0]

        try:
            ns.save() # This calls clean
        except Exception, e:
            return self.get(self, request, *args, **kwargs)

        # Success. Redirect.
        return redirect( ns )

    def get_context_data(self, **kwargs):
        context = super(NSCreateView, self).get_context_data(**kwargs)
        context['form_title'] = "Create NS"
        return context

class NSUpdateView(NSView, UpdateView):
    template_name = "ns_form.html"
    qeuryset = Nameserver.objects.all()

    def get_form(self, form_class):
        form = super(NSUpdateView, self).get_form( form_class)
        # This is where filtering domain selection should take place.
        # form.fields['domain'].queryset = Domain.objects.filter( name = 'foo.com')
        # This ^ line will change the query set to something controllable
        # find user credentials in self.request
        return form

    # Handle this post manually.
    def post(self, request, *args, **kwargs ):
        ns = get_object_or_404( Nameserver, pk=kwargs.get('pk', 0))
        server = request.POST.get('server', False)
        domain_pk = request.POST.get('domain', False)

        if server:
            ns.server = server
        if domain_pk:
            try:
                domain = Domain.objects.get( pk = int(domain_pk) )
            except ValueError, e:
                messages.error( request, "Something went very wrong. domain was not type int." )
                return self.get(self, request, *args, **kwargs)
            ns.domain = domain

        # If ns needs a glue record, find it. It we can't find it return and error.
        if _needs_glue( ns ):
            glue_label = server.split('.')[0] # foo.com -> foo
            # This will cause a problem if there is more than one dns name here.
            glue = AddressRecord.objects.filter( label = glue_label, domain = domain )
            if not glue:
                form = NameserverForm( request.POST )
                return render( request, "ns_form.html", {'form': form } )
            else:
                ns.glue = glue[0]

        try:
            ns.save() # This calls clean
        except ValidationError, e:
            return self.get(self, request, *args, **kwargs)

        # Success. Redirect.
        return redirect( ns )

    def get_context_data(self, **kwargs):
        context = super(NSUpdateView, self).get_context_data(**kwargs)
        context['form_title'] = "Update NS"
        return context
