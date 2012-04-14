from django import forms
from django.shortcuts import render_to_response

from cyder.search.utils import _build_queries
import pdb


class DNSSearch(forms.Form):
    fqdn = forms.CharField(required=False)
    ip = forms.CharField(required=False)
    search_all = forms.BooleanField(required=False, initial=True)
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
    ip_str = form.cleaned_data['ip']

    if not ip_str and not fqdn:
        return render_to_response('search/dns_search.html', {'form': form, 'request':request})

    if not (form.cleaned_data['domain'] or form.cleaned_data['reverse_domain'] or
            form.cleaned_data['mx'] or form.cleaned_data['srv'] or
            form.cleaned_data['txt'] or form.cleaned_data['cname'] or
            form.cleaned_data['address_record'] or form.cleaned_data['ptr']):
        # They didn't select anything. Search all the things!
        form.cleaned_data['search_all'] = True

    if form.cleaned_data['search_all']:
        qsets = _build_queries(fqdn, ip=ip_str)
        return render_to_response('search/dns_results.html', {'results': qsets,
                                  'all':True, 'request':request})

    # Build a search
    qsets = _build_queries(fqdn, form.cleaned_data['domain'],
                        form.cleaned_data['reverse_domain'],
                        form.cleaned_data['mx'], form.cleaned_data['srv'],
                        form.cleaned_data['txt'], form.cleaned_data['cname'],
                        form.cleaned_data['address_record'],
                        form.cleaned_data['ptr'], ip=ip_str)

    return render_to_response('search/dns_results.html', {'results': qsets,
            'all': False, 'request': request})



