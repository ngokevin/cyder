# Create your views here.
from django.shortcuts import render_to_response, render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.forms import ValidationError

from django import forms

import pdb
from cyder.cydns.soa.models import SOA
from cyder.cydns.reverse_domain.models import ReverseDomain, boot_strap_add_ipv6_reverse_domain
from cyder.cydns.reverse_domain.forms import ReverseDomainForm, ReverseDomainUpdateForm, BootStrapForm
from cyder.cydns.common.views import CommonDeleteView



class ReverseDomainView(object):
    queryset            = ReverseDomain.objects.all()
    form_class          = ReverseDomainForm

class ReverseDomainDeleteView(ReverseDomainView, CommonDeleteView):
    """ """

class ReverseDomainListView(ReverseDomainView, ListView):
    template_name       = "reverse_domain_list.html"
    context_object_name = "reverse_domains"

class ReverseDomainDetailView(ReverseDomainView, DetailView):
    context_object_name = "reverse_domain"
    template_name       = "reverse_domain_detail.html"

class ReverseDomainView(object):
    model = ReverseDomain
    queryset = ReverseDomain.objects.all()

class ReverseDomainCreateView(ReverseDomainView, CreateView):
    form_class = ReverseDomainForm
    template_name = "reverse_domain_form.html"
    context_object_name = "reverse_domain_form"

    def post( self, request, *args, **kwargs ):
        reverse_domain_form = ReverseDomainForm(request.POST)
        # Try to create the reverse_domain. Catch all exceptions.
        try:
            reverse_domain = reverse_domain_form.save(commit=False)
            if reverse_domain_form.cleaned_data['inherit_soa'] and reverse_domain.master_reverse_domain:
                reverse_domain.soa = reverse_domain.master_reverse_domain.soa
            reverse_domain.save()
        except ValidationError, e:
            return render( request, "reverse_domain_form.html", { "reverse_domain_form": reverse_domain_form } )

        # Success. Redirect.
        messages.success(request, '%s was successfully created.' % (reverse_domain.name))
        return redirect( reverse_domain )


class ReverseDomainUpdateView(ReverseDomainView, UpdateView):
    form_class = ReverseDomainUpdateForm
    template_name = "reverse_domain_update.html"
    context_object_name = "reverse_domain"

    def post(self, request, *args, **kwargs):
        reverse_domain = get_object_or_404( ReverseDomain, pk = kwargs.get('pk',0 ))
        try:
            reverse_domain_form = ReverseDomainUpdateForm(request.POST)
            new_soa_pk = reverse_domain_form.data.get('soa', None)
            if new_soa_pk:
                new_soa = SOA.objects.get( pk = new_soa_pk )
                reverse_domain.soa = new_soa

            if reverse_domain.soa and not new_soa_pk:
                reverse_domain.soa = None

            if reverse_domain_form.data.get('inherit_soa', False) and reverse_domain.master_reverse_domain:
                reverse_domain.soa = reverse_domain.master_reverse_domain.soa

            reverse_domain.save() # Major exception handling logic goes here.
        except ValueError, e:
            reverse_domain_form = ReverseDomainUpdateForm(instance=reverse_domain)
            messages.error( request, e.__str__() )
            return render( request, "reverse_domain_update.html", { "reverse_domain_form": reverse_domain_form } )

        messages.success(request, '%s was successfully updated.' % (reverse_domain.name))
        return redirect( reverse_domain )

    def get(self, request, *args, **kwargs):
        ret = super(ReverseDomainUpdateView, self).get(request, *args, **kwargs)
        return ret

def bootstrap_ipv6(request):
    if request.method == 'POST':
        bootstrap_form = BootStrapForm(request.POST)
        if bootstrap_form.is_valid():
            if bootstrap_form.data['soa'] == '':
                soa = None
            else:
                soa = get_object_or_404(SOA, pk = bootstrap_form.data['soa'])
            try:
                reverse_domain = boot_strap_add_ipv6_reverse_domain( bootstrap_form.cleaned_data['name'], soa = soa )
            except ValidationError, e:
                messages.error( request, e.__str__() )
                return render( request, 'bootstrap_ipv6.html', {'bootstrap_form': bootstrap_form} )
        else:
            return render( request, 'bootstrap_ipv6.html', {'bootstrap_form': bootstrap_form} )


        # Success redirect to the last domain created.
        messages.success(request, "Success! Bootstrap complete. You are now looking at the leaf reverse domain.")
        return redirect(reverse_domain)

    else:
        bootstrap_form = BootStrapForm()
        return render( request, 'bootstrap_ipv6.html', {'bootstrap_form': bootstrap_form} )



def inheirit_soa(request, pk):
    reverse_domain = get_object_or_404( ReverseDomain, pk = pk )
    if request.method == 'POST':
        if reverse_domain.master_reverse_domain:
            reverse_domain.soa = reverse_domain.master_reverse_domain.soa
            reverse_domain.save() # Clean gets called in save()
            messages.success(request, '%s was successfully updated.' % (reverse_domain.name))
    return redirect('/cyder/cydns/reverse_domain')


