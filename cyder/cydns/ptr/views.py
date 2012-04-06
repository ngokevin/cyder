from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render

from cyder.cydns.common.views import CommonCreateView
from cyder.cydns.common.views import CommonDeleteView
from cyder.cydns.common.views import CommonDetailView
from cyder.cydns.common.views import CommonListView
from cyder.cydns.common.views import CommonUpdateView
from cyder.cydns.ip.forms import IpForm
from cyder.cydns.ptr.forms import PTRForm
from cyder.cydns.ptr.models import PTR


class PTRView(object):
    model = PTR
    form_class = PTRForm
    queryset = PTR.objects.all()


class PTRDeleteView(PTRView, CommonDeleteView):
    """ """


class PTRDetailView(PTRView, CommonDetailView):
    """ """
    template_name = "ptr/detail.html"


class PTRCreateView(PTRView, CommonCreateView):
    """ """


class PTRUpdateView(PTRView, CommonUpdateView):
    """ """


class PTRListView(PTRView, CommonListView):
    """ """
    template_name = "ptr/list.html"
