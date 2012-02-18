# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from session_csrf import anonymous_csrf
from django.forms.formsets import formset_factory
from django.contrib import messages


from cyder.cydns.domain.models import Domain, DomainForm, DomainUpdateForm, DomainHasChildDomains
from cyder.cydns.domain.models import DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.soa.models import SOA
from cyder.cydns.mx.models import MX
from cyder.cydns.common.utils import tablefy

import pdb
from operator import itemgetter

DNS_BASE = '/cyder/cydns'

@csrf_exempt
def domain_list(request):
    domains = Domain.objects.all()
    return render( request, 'domain_list.html', {'domains': domains} )

@csrf_exempt
def domain_create(request):
    if request.method == 'POST':
        domain_form = DomainForm(request.POST)
        # Try to create the domain. Catch all exceptions.
        try:
            # If there were errors collect them and render the page again, displaying the errors.
            if domain_form.errors:
                errors = ""
                for k,v in domain_form.errors.items():
                    for reason in v:
                        errors += k+": "+reason+"\n"
                messages.error( request, errors )
                return render( request, "domain_create.html", { "domain_form": domain_form } )
            domain_form.is_valid()
            domain = domain_form.save(commit=False)
            if domain_form.cleaned_data['inherit_soa'] and domain.master_domain:
                domain.soa = domain.master_domain.soa
            domain.save()
        except Exception, e:
            messages.error( request, e.__str__() )
            return render( request, "domain_create.html", { "domain_form": domain_form } )

        # Success. Redirect to
        messages.success(request, '%s was successfully created.' % (domain.name))
        domain_update_form = DomainUpdateForm(instance=domain)
        c = RequestContext(request)
        resp_param = ("domain_update.html", { 'domain_form': domain_update_form })
        return redirect('cyder.cydns.domain.views.domain_update', pk = domain.pk )
    else:
        domain_form = DomainForm()
        c = RequestContext(request)
        resp_param = ("domain_create.html", { "domain_form": domain_form })
        return render_to_response(*resp_param, context_instance = c )


@csrf_exempt
def domain_update(request, pk):
    # Construct tables of the child objects.
    tables = []
    #gen_table( AddressRecord.objects.all(), ['__fqdn__', 'ip'] '/cyder/address_record/%s/update' )
    domain = Domain.objects.get( pk = pk )
    if request.method == 'POST':
        try:
            domain_form = DomainUpdateForm(request.POST)
            if domain_form.data.get('delete', False):
                domain.delete()
                messages.success(request, '%s was successfully deleted.' % (domain.name))
                return redirect('cyder.cydns.domain.views.domain_list')
            new_soa_pk = domain_form.data.get('soa', None)
            if new_soa_pk:
                new_soa = SOA.objects.get( pk = new_soa_pk )
                domain.soa = new_soa

            if domain.soa and not new_soa_pk:
                domain.soa = None

            if domain_form.data.get('inherit_soa', False) and domain.master_domain:
                domain.soa = domain.master_domain.soa

            domain.save() # Major exception handling logic goes here.
        except Exception, e:
            domain_form = DomainUpdateForm(instance=domain)
            messages.error( request, e.__str__() )
            return render( request, "domain_update.html", { "domain_form": domain_form } )

        messages.success(request, '%s was successfully updated.' % (domain.name))

        domain_form = DomainUpdateForm(instance=domain)
        c = RequestContext(request)
        resp_param = ("domain_update.html", { "domain_form": domain_form })
        return render_to_response(*resp_param, context_instance = c )
    else:
        address_objects = AddressRecord.objects.filter( domain = domain )
        adr_headers, adr_matrix, adr_urls = tablefy( address_objects )

        mx_objects = MX.objects.filter( domain = domain )
        mx_headers, mx_matrix, mx_urls = tablefy( mx_objects )

        domain_form = DomainUpdateForm(instance=domain)
        c = RequestContext(request)

        params = {
                "domain_form": domain_form,
                # A and AAAA
                "address_headers": adr_headers,
                "address_matrix": adr_matrix,
                "address_urls": adr_urls,
                # MX
                "mx_headers": mx_headers,
                "mx_matrix": mx_matrix,
                "mx_urls": mx_urls
                 }
        resp_param = ("domain_update.html", params )
        return render_to_response(*resp_param, context_instance = c )

