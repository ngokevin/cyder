# Create your views here.
# Create your views here.
from cyder.cydns.common.views import CommonDetailView, CommonCreateView, CommonUpdateView, CommonListView, CommonDeleteView
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from cyder.cydns.ptr.models import PTR
from cyder.cydns.ptr.forms import PTRForm
from cyder.cydns.ip.forms import IpForm
import pdb

class PTRView(object):
    model      = PTR
    form_class = PTRForm
    queryset   = PTR.objects.all()

class PTRDeleteView(PTRView, CommonDeleteView):
    """ """

class PTRDetailView(PTRView, CommonDetailView):
    """ """

class PTRCreateView(PTRView, CommonCreateView):
    """ """
    def post( self, request, *args, **kwargs ):
        ip_form = IpForm( request.POST )
        ptr_form = PTRForm( request.POST )
        try:
            ip = ip_form.save()
            ptr = ptr_form.save(commit = False)
            ptr.ip = ip
            ptr.ip_type = ip.ip_type
            ptr.save()
        except ValueError, e:
            return render( request, "ptr_create.html", { "ptr_form": ptr_form, "ip_form": ip_form } )

        messages.success( request, "Successfully Created PTR Record." )
        return redirect( ptr )

    def get( self, request, *args, **kwargs ):
        ip_form = IpForm()
        ptr_form = PTRForm()
        return render( request, "ptr_create.html", { "ptr_form": ptr_form, "ip_form": ip_form } )

class PTRUpdateView(PTRView, CommonUpdateView):
    """ """

class PTRListView(PTRView, CommonListView):
    """ """
