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
from django import forms

import pdb
from cyder.cydns.soa.models import SOA
from cyder.cydns.reverse_domain.models import ReverseDomain, ReverseDomainForm, ReverseDomainUpdateForm
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

class BootStrapForm( forms.Form ):
    name = forms.CharField(max_length=100)
    soa  = forms.ChoiceField( required=False )

    def __init__(self, *args, **kwargs):
        super(BootStrapForm, self).__init__(*args, **kwargs)
        # Update the form with recent data
        choices = [('','-----------' )]+[ (soa,soa) for soa in SOA.objects.all() ]
        self['soa'].field._choices += choices


@csrf_exempt
def bootstrap_ipv6(request):
    if request.method == 'POST':
        bootstrap_form = BootStrapForm(request.POST)
        if bootstrap_form.is_valid():
            try:
                reverse_domain = boot_strap_add_ipv6_reverse_domain( bootstrap_form.cleaned_data['name'] )
            except Exception, e:
                messages.error( request, e.__str__() )
                return render( request, 'bootstrap_ipv6.html', {'bootstrap_form': bootstrap_form} )

        # Success redirect to the last domain created.
        reverse_domain_form = ReverseDomainUpdateForm(instance=reverse_domain)
        c = RequestContext(request)
        resp_param = ("reverse_domain_update.html", { "reverse_domain_form": reverse_domain_form })
        return render_to_response(*resp_param, context_instance = c )

    else:
        bootstrap_form = BootStrapForm()
        return render( request, 'bootstrap_ipv6.html', {'bootstrap_form': bootstrap_form} )


@csrf_exempt
def reverse_domain_list(request):
    reverse_domains = ReverseDomain.objects.all()
    return render( request, 'reverse_domain_list.html', {'reverse_domains': reverse_domains} )

@csrf_exempt
def inheirit_soa(request, pk):
    reverse_domain = ReverseDomain.objects.get( pk = pk )
    if request.method == 'POST':
        if reverse_domain.master_reverse_domain:
            reverse_domain.soa = reverse_domain.master_reverse_domain.soa
            reverse_domain.save() # Clean gets called in save()
            messages.success(request, '%s was successfully updated.' % (reverse_domain.name))
    return redirect('cyder.cydns.reverse_domain.views.reverse_domain_list' )


@csrf_exempt
def reverse_domain_create(request):
    if request.method == 'POST':
        reverse_domain_form = ReverseDomainForm(request.POST)
        # Try to create the reverse_domain. Catch all exceptions.
        try:
            reverse_domain_form.is_valid()
            reverse_domain = reverse_domain_form.save(commit=False)
            if reverse_domain_form.cleaned_data['inherit_soa'] and reverse_domain.master_reverse_domain:
                reverse_domain.soa = reverse_domain.master_reverse_domain.soa
            reverse_domain.save()
        except Exception, e:
            messages.error( request, e.__str__() )
            return render( request, "reverse_domain_create.html", { "reverse_domain_form": reverse_domain_form } )

        # Success. Redirect.
        messages.success(request, '%s was successfully created.' % (reverse_domain.name))
        reverse_domain_update_form = ReverseDomainUpdateForm(instance=reverse_domain)
        c = RequestContext(request)
        resp_param = ("reverse_domain_update.html", { 'reverse_domain_form': reverse_domain_update_form })
        return redirect('cyder.cydns.reverse_domain.views.reverse_domain_update', pk = reverse_domain.pk )
    else:
        reverse_domain_form = ReverseDomainForm()
        c = RequestContext(request)
        resp_param = ("reverse_domain_create.html", { "reverse_domain_form": reverse_domain_form })
        return render_to_response(*resp_param, context_instance = c )


@csrf_exempt
def reverse_domain_update(request, pk):
    reverse_domain = ReverseDomain.objects.get( pk = pk )
    if request.method == 'POST':
        try:
            reverse_domain_form = ReverseDomainUpdateForm(request.POST)
            if reverse_domain_form.data.get('delete', False):
                reverse_domain.delete()
                messages.success(request, '%s was successfully deleted.' % (reverse_domain.name))
                return redirect('cyder.cydns.reverse_domain.views.reverse_domain_list')
            new_soa_pk = reverse_domain_form.data.get('soa', None)
            if new_soa_pk:
                new_soa = SOA.objects.get( pk = new_soa_pk )
                reverse_domain.soa = new_soa

            if reverse_domain.soa and not new_soa_pk:
                reverse_domain.soa = None

            if reverse_domain_form.data.get('inherit_soa', False) and reverse_domain.master_reverse_domain:
                reverse_domain.soa = reverse_domain.master_reverse_domain.soa

            reverse_domain.save() # Major exception handling logic goes here.
        except Exception, e:
            reverse_domain_form = ReverseDomainUpdateForm(instance=reverse_domain)
            messages.error( request, e.__str__() )
            return render( request, "reverse_domain_update.html", { "reverse_domain_form": reverse_domain_form } )

        messages.success(request, '%s was successfully updated.' % (reverse_domain.name))

        reverse_domain_form = ReverseDomainUpdateForm(instance=reverse_domain)
        c = RequestContext(request)
        resp_param = ("reverse_domain_update.html", { "reverse_domain_form": reverse_domain_form })
        return render_to_response(*resp_param, context_instance = c )
    else:
        reverse_domain_form = ReverseDomainUpdateForm(instance=reverse_domain)
        c = RequestContext(request)
        resp_param = ("reverse_domain_update.html", { "reverse_domain_form": reverse_domain_form })
        return render_to_response(*resp_param, context_instance = c )
