from django import forms
from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render, render_to_response
from django.views.generic import DetailView, ListView, CreateView, UpdateView

from cyder.cydns.common.utils import tablefy
from cyder.cydns.common.views import CommonDeleteView
from cyder.cydns.nameserver.reverse_nameserver.models import ReverseNameserver
from cyder.cydns.reverse_domain.models import boot_strap_ipv6_reverse_domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.reverse_domain.forms import BootStrapForm
from cyder.cydns.reverse_domain.forms import ReverseDomainForm
from cyder.cydns.reverse_domain.forms import ReverseDomainUpdateForm
from cyder.cydns.soa.models import SOA


class ReverseDomainView(object):
    queryset = ReverseDomain.objects.all()
    form_class = ReverseDomainForm


class ReverseDomainDeleteView(ReverseDomainView, CommonDeleteView):
    """ """


class ReverseDomainListView(ReverseDomainView, ListView):
    template_name = "reverse_domain/reverse_domain_list.html"
    context_object_name = "reverse_domains"


class ReverseDomainDetailView(ReverseDomainView, DetailView):
    context_object_name = "reverse_domain"
    template_name = "reverse_domain/reverse_domain_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ReverseDomainDetailView, self).get_context_data(
                                                                **kwargs)

        reverse_domain = kwargs.get('object', False)
        if not reverse_domain:
            return context
        # TODO
        # This process can be generalized. It's not very high priority.
        revns_objects = ReverseNameserver.objects.filter(
                                        reverse_domain=reverse_domain)

        revns_headers, revns_matrix, revns_urls = tablefy(revns_objects)

        # Join the two dicts
        context = dict({
                    # NS
                    "revns_headers": revns_headers,
                    "revns_matrix": revns_matrix,
                    "revns_urls": revns_urls,
                        }.items() + context.items())
        return context


class ReverseDomainView(object):
    model = ReverseDomain
    queryset = ReverseDomain.objects.all()


class ReverseDomainCreateView(ReverseDomainView, CreateView):
    form_class = ReverseDomainForm
    template_name = "reverse_domain/form.html"
    context_object_name = "reverse_domain_form"

    def post(self, request, *args, **kwargs):
        reverse_domain_form = ReverseDomainForm(request.POST)
        # Try to create the reverse_domain. Catch all exceptions.
        try:
            reverse_domain = reverse_domain_form.save(commit=False)
            if (reverse_domain_form.cleaned_data['inherit_soa'] and
                reverse_domain.master_reverse_domain):
                reverse_domain.soa = reverse_domain.master_reverse_domain.soa

            reverse_domain.save()
        except ValidationError, e:
            return render(request, "reverse_domain/form.html",
                          {"reverse_domain_form": reverse_domain_form})

        # Success. Redirect.
        messages.success(request, '{0} was successfully created.'.
                         format(reverse_domain.name))

        return redirect(reverse_domain)


class ReverseDomainUpdateView(ReverseDomainView, UpdateView):
    form_class = ReverseDomainUpdateForm
    template_name = "reverse_domain/update.html"
    context_object_name = "reverse_domain"

    def post(self, request, *args, **kwargs):
        reverse_domain = get_object_or_404(ReverseDomain,
                                           pk=kwargs.get('pk', 0))
        try:
            reverse_domain_form = ReverseDomainUpdateForm(request.POST)
            new_soa_pk = reverse_domain_form.data.get('soa', None)
            if new_soa_pk:
                new_soa = SOA.objects.get(pk=new_soa_pk)
                reverse_domain.soa = new_soa

            if reverse_domain.soa and not new_soa_pk:
                reverse_domain.soa = None

            if (reverse_domain_form.data.get('inherit_soa', False) and
                reverse_domain.master_reverse_domain):
                reverse_domain.soa = reverse_domain.master_reverse_domain.soa
            reverse_domain.save()  # Major exception handling logic
                                   # happens here.
        except ValueError, e:
            rev_domain_form = ReverseDomainUpdateForm(instance=reverse_domain)
            messages.error(request, str(e))
            return render(request, "reverse_domain/update.html",
                          {"reverse_domain_form": rev_domain_form})

        messages.success(request, '{0} was successfully updated.'.
                         format(reverse_domain.name))
        return redirect(reverse_domain)

    def get(self, request, *args, **kwargs):
        ret = super(ReverseDomainUpdateView, self).get(request,
                                                       *args, **kwargs)
        return ret


def bootstrap_ipv6(request):
    if request.method == 'POST':
        bootstrap_form = BootStrapForm(request.POST)
        if bootstrap_form.is_valid():
            if bootstrap_form.data['soa'] == '':
                soa = None
            else:
                soa = get_object_or_404(SOA, pk=bootstrap_form.data['soa'])
            try:
                reverse_domain = boot_strap_ipv6_reverse_domain(
                                    bootstrap_form.cleaned_data['name'],
                                    soa=soa)
            except ValidationError, e:
                messages.error(request, str(e))
                return render(request, 'reverse_domain/bootstrap_ipv6.html',
                              {'bootstrap_form': bootstrap_form})
        else:
            return render(request, 'reverse_domain/bootstrap_ipv6.html',
                          {'bootstrap_form': bootstrap_form})

        # Success redirect to the last domain created.
        messages.success(request, "Success! Bootstrap complete. You are "
                         "now looking at the leaf reverse domain.")
        return redirect(reverse_domain)

    else:
        bootstrap_form = BootStrapForm()
        return render(request, 'reverse_domain/bootstrap_ipv6.html',
                      {'bootstrap_form': bootstrap_form})


def inheirit_soa(request, pk):
    reverse_domain = get_object_or_404(ReverseDomain, pk=pk)
    if request.method == 'POST':
        if reverse_domain.master_reverse_domain:
            reverse_domain.soa = reverse_domain.master_reverse_domain.soa
            reverse_domain.save()
            messages.success(request, '{0} was successfully updated.'.
                             format(reverse_domain.name))
    return redirect('/cyder/cydns/reverse_domain')
