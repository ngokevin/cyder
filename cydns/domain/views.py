# Create your views here.

from django.shortcuts import render_to_response, render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.forms import ValidationError


from cyder.cydns.domain.models import Domain, DomainHasChildDomains
from cyder.cydns.domain.forms import DomainForm, DomainUpdateForm
from cyder.cydns.domain.models import DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.common.utils import tablefy
from cyder.cydns.common.views import CommonDeleteView

from cyder.cydns.soa.models import SOA
from cyder.cydns.mx.models import MX
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.cydns.cname.models import CNAME
from cyder.cydns.ptr.models import PTR

import pdb
from operator import itemgetter

class DomainView(object):
    queryset            = Domain.objects.all()

class DomainDeleteView(DomainView, CommonDeleteView):
    """ """

class DomainListView(DomainView, ListView):
    template_name       = "domain_list.html"
    context_object_name = "domains"


class DomainDetailView(DomainView, DetailView):
    context_object_name = "domain"
    template_name       = "domain_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        domain = kwargs.get('object', False)
        if not domain:
            return context
        # TODO
        # This process can be generalized. It's not very high priority.
        address_objects = AddressRecord.objects.filter( domain = domain )
        adr_headers, adr_matrix, adr_urls = tablefy( address_objects )

        mx_objects = MX.objects.filter( domain = domain )
        mx_headers, mx_matrix, mx_urls = tablefy( mx_objects )

        srv_objects = SRV.objects.filter( domain = domain )
        srv_headers, srv_matrix, srv_urls = tablefy( srv_objects )

        txt_objects = TXT.objects.filter( domain = domain )
        txt_headers, txt_matrix, txt_urls = tablefy( txt_objects )

        cname_objects = CNAME.objects.filter( domain = domain )
        cname_headers, cname_matrix, cname_urls = tablefy( cname_objects )

        ptr_objects = PTR.objects.filter( domain = domain )
        ptr_headers, ptr_matrix, ptr_urls = tablefy( ptr_objects )

        # Join the two dicts
        context = dict( {
                    # A and AAAA
                    "address_headers": adr_headers,
                    "address_matrix": adr_matrix,
                    "address_urls": adr_urls,
                    # MX
                    "mx_headers": mx_headers,
                    "mx_matrix": mx_matrix,
                    "mx_urls": mx_urls,
                    # SRV
                    "srv_headers": srv_headers,
                    "srv_matrix": srv_matrix,
                    "srv_urls": srv_urls,
                    # TXT
                    "txt_headers": txt_headers,
                    "txt_matrix": txt_matrix,
                    "txt_urls": txt_urls,

                    # CNAME
                    "cname_headers": cname_headers,
                    "cname_matrix": cname_matrix,
                    "cname_urls": cname_urls,

                    # PTR
                    "ptr_headers": ptr_headers,
                    "ptr_matrix": ptr_matrix,
                    "ptr_urls": ptr_urls
                        }.items() + context.items() )
        return context

class DomainView(object):
    model = Domain
    queryset = Domain.objects.all()

class DomainCreateView(DomainView, CreateView):
    model_form = DomainForm
    template_name = "domain_form.html"

    def post( self, request, *args, **kwargs ):
        domain_form = DomainForm(request.POST)
        # Try to create the domain. Catch all exceptions.
        try:
            domain = domain_form.save(commit=False)
        except ValueError, e:
            return render( request, "domain_form.html", { 'domain_form': domain_form } )

        if domain_form.cleaned_data['inherit_soa'] and domain.master_domain:
            domain.soa = domain.master_domain.soa
        try:
            domain.save()
        except ValidationError, e:
            return render( request, "domain_form.html", { 'domain_form': domain_form } )
        # Success. Redirect.
        messages.success(request, '%s was successfully created.' % (domain.name))
        return redirect( domain )

    def get( self, request, *args, **kwargs ):
        domain_form = DomainForm()
        return render( request, "domain_form.html", { 'domain_form': domain_form } )


class DomainUpdateView( DomainView, UpdateView ):
    form_class = DomainUpdateForm
    template_name = "domain_update.html"
    context_object_name = "domain"

    def post( self, request, *args, **kwargs ):
        domain = get_object_or_404( Domain, pk = kwargs.get('pk',0) )
        try:
            domain_form = DomainUpdateForm(request.POST)
            new_soa_pk = domain_form.data.get('soa', None)
            if new_soa_pk:
                new_soa = SOA.objects.get( pk = new_soa_pk )
                domain.soa = new_soa

            if domain.soa and not new_soa_pk:
                domain.soa = None

            if domain_form.data.get('inherit_soa', False) and domain.master_domain:
                domain.soa = domain.master_domain.soa

            domain.save() # Major exception handling logic goes here.
        except ValidationError, e:
            domain_form = DomainUpdateForm(instance=domain)
            messages.error( request, e.__str__() )
            return render( request, "domain_update.html", { "domain_form": domain_form } )

        messages.success(request, '%s was successfully updated.' % (domain.name))

        return redirect( domain )
