from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render

from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsListView
from cyder.cydns.views import CydnsUpdateView
from cyder.cydns.ip.forms import IpForm
from cyder.cydns.ptr.forms import PTRForm
from cyder.cydns.ptr.models import PTR


class PTRView(object):
    model = PTR
    form_class = PTRForm
    queryset = PTR.objects.all()


class PTRDeleteView(PTRView, CydnsDeleteView):
    """ """


class PTRDetailView(PTRView, CydnsDetailView):
    """ """
    template_name = "ptr/ptr_detail.html"


class PTRCreateView(PTRView, CydnsCreateView):
    """ """


class PTRUpdateView(PTRView, CydnsUpdateView):
    """ """


class PTRListView(PTRView, CydnsListView):
    """ """
    template_name = "ptr/ptr_list.html"
