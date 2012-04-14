from django.shortcuts import render_to_response

from cyder.cydns.nameserver.nameserver.forms import NameserverForm
from cyder.cydns.nameserver.nameserver.forms import NSDelegated
from cyder.cydns.nameserver.nameserver.models import Nameserver
from cyder.cydns.nameserver.views import *

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.domain.models import Domain


class NSView(object):
    model = Nameserver
    form_class = NameserverForm
    queryset = Nameserver.objects.all()


class NSDeleteView(NSView, CydnsDeleteView):
    """ """


class NSDetailView(NSView, CydnsDetailView):
    template_name = "nameserver/nameserver_detail.html"


class NSListView(NSView, CydnsListView):
    """ """
    template_name = "nameserver/nameserver_list.html"


class NSCreateView(NSView, CydnsCreateView):
    """ """


class NSUpdateView(NSView, CydnsUpdateView):
    """ """

def create_ns_delegated(request, domain):
    if request.method == "POST":
        form = NSDelegated(request.POST)
        domain = Domain.objects.get(pk=domain)
        if not domain:
            pass  # Fall through. Maybe send a message saying no domain?
        elif form.is_valid():
            server = form.cleaned_data['server']
            ip_str = form.cleaned_data['server_ip_address']
            was_delegated = domain.delegated
            if was_delegated:
                # Quickly and transperently Un-delegate the domain so we
                # can add an address record.
                domain.delegated = False
                domain.save()
            if was_delegated:
                # Reset delegation status
                domain.delegated = True
                domain.save()

        else:
            pass  # Fall through
    # Everything else get's the blank form
    form = NSDelegated()
    return render_to_response("nameserver/ns_delegated.html",
            {'form': form, 'request': request})

