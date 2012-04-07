from django import forms
from django.shortcuts import render_to_response

from cyder.cysearch.utils import fqdn_search
import pdb


class DNSSearch(forms.Form):
    fqdn = forms.CharField()
    search_all = forms.BooleanField(required=False)
    domain = forms.BooleanField(required=False)
    reverse_domain = forms.BooleanField(required=False)
    mx = forms.BooleanField(required=False)
    srv = forms.BooleanField(required=False)
    txt = forms.BooleanField(required=False)
    cname = forms.BooleanField(required=False)
    address_record = forms.BooleanField(required=False)
    ptr = forms.BooleanField(required=False)

def dns_search(request):
    form = DNSSearch()
    return render_to_response('search/dns_search.html', {'form': form, 'request':request})

def dns_results(request):
    if request.method != "GET":
        return render_to_response('search/dns_search.html', {'form': form, 'request':request})
    form = DNSSearch(request.GET)
    if not form.is_valid():
        return render_to_response('search/dns_search.html', {'form': form, 'request':request})

    fqdn = form.cleaned_data['fqdn']
    if form.cleaned_data['search_all']:
        qsets = fqdn_search(fqdn)
        return render_to_response('search/dns_results.html', {'results': qsets,
                                  'all':True, 'request':request})

    # Build a search
    qsets = fqdn_search(fqdn, form.cleaned_data['domain'],
                        form.cleaned_data['reverse_domain'],
                        form.cleaned_data['mx'], form.cleaned_data['srv'],
                        form.cleaned_data['txt'], form.cleaned_data['cname'],
                        form.cleaned_data['address_record'],
                        form.cleaned_data['ptr'])
    return render_to_response('search/dns_results.html', {'results': qsets, 'all': False, 'request':request})



