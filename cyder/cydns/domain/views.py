from operator import itemgetter

from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic import UpdateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import CreateView

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.utils import tablefy
from cyder.cydns.views import CydnsCreateView, CydnsDeleteView, CydnsListView
from cyder.cydns.domain.models import Domain
from cyder.cydns.domain.forms import DomainForm, DomainUpdateForm
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT


class DomainView(object):
    model = Domain
    queryset = Domain.objects.all().order_by('name')
    form_class = DomainForm


class DomainDeleteView(DomainView, CydnsDeleteView):
    """ """


class DomainListView(DomainView, CydnsListView):
    """ """
    template_name = "domain/domain_list.html"


class DomainDetailView(DomainView, DetailView):
    context_object_name = "domain"
    template_name = "domain/domain_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        domain = kwargs.get('object', False)
        if not domain:
            return context
        # TODO
        # This process can be generalized. It's not very high priority.
        address_objects = domain.addressrecord_set.all()
        adr_headers, adr_matrix, adr_urls = tablefy(address_objects)

        mx_objects = domain.mx_set.all()
        mx_headers, mx_matrix, mx_urls = tablefy(mx_objects)

        srv_objects = domain.srv_set.all()
        srv_headers, srv_matrix, srv_urls = tablefy(srv_objects)

        txt_objects = domain.txt_set.all()
        txt_headers, txt_matrix, txt_urls = tablefy(txt_objects)

        cname_objects = domain.cname_set.all()
        cname_headers, cname_matrix, cname_urls = tablefy(cname_objects)

        ptr_objects = domain.ptr_set.all()
        ptr_headers, ptr_matrix, ptr_urls = tablefy(ptr_objects)

        ns_objects = domain.nameserver_set.all()
        ns_headers, ns_matrix, ns_urls = tablefy(ns_objects)

        # Join the two dicts
        context = dict({
                    # NS
                    "ns_headers": ns_headers,
                    "ns_matrix": ns_matrix,
                    "ns_urls": ns_urls,
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
                       }.items() + context.items())
        return context


class DomainCreateView(CreateView, DomainView):
    model_form = DomainForm
    template_name = "domain/domain_form.html"

    def post(self, request, *args, **kwargs):
        domain_form = DomainForm(request.POST)
        # Try to create the domain. Catch all exceptions.
        try:
            domain = domain_form.save(commit=False)
        except ValueError, e:
            return render(request, "domain/domain_form.html", {'form': domain_form})

        if domain_form.cleaned_data['inherit_soa'] and domain.master_domain:
            domain.soa = domain.master_domain.soa
        try:
            domain.save()
        except ValidationError, e:
            return render(request, "domain/domain_form.html", {'form': domain_form})
        # Success. Redirect.
        messages.success(request, "{0} was successfully created.".
                         format(domain.name))
        return redirect(domain)

    def get(self, request, *args, **kwargs):
        domain_form = DomainForm()
        return render(request, "domain/domain_form.html", {'form': domain_form})


class DomainUpdateView(DomainView, UpdateView):
    form_class = DomainUpdateForm
    template_name = "domain/domain_update.html"
    context_object_name = "domain"

    def post(self, request, *args, **kwargs):
        domain = get_object_or_404(Domain, pk=kwargs.get('pk', 0))
        try:
            domain_form = DomainUpdateForm(request.POST)
            new_soa_pk = domain_form.data.get('soa', None)
            delegation_status = domain_form.data.get('delegated', False)

            if new_soa_pk:
                new_soa = get_object_or_404(SOA, pk=new_soa_pk)
            else:
                new_soa = None

            if delegation_status == 'on':
                new_delegation_status = True
            else:
                new_delegation_status = False

            updated = False
            if domain.soa != new_soa:
                domain.soa = new_soa
                updated = True
            if domain.delegated != new_delegation_status:
                domain.delegated = new_delegation_status
                updated = True

            if updated:
                domain.save()  # Major exception handling logic goes here.
        except ValidationError, e:
            domain_form = DomainUpdateForm(instance=domain)
            messages.error(request, str(e))
            return render(request, "domain/domain_update.html", {"form": domain_form})

        messages.success(request, '{0} was successfully updated.'.
                         format(domain.name))

        return redirect(domain)
