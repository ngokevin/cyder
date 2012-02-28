# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.forms import ValidationError
from django.views.generic import DetailView, CreateView, UpdateView

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.address_record.forms import AddressRecordForm
from cyder.cydns.common.views import CommonDeleteView, CommonDetailView
from cyder.cydns.ip.models import Ip
from cyder.cydns.ip.forms import IpForm

import pdb

class AddressRecordView(object):
    model = AddressRecord
    form_class = AddressRecordForm
    queryset = AddressRecord.objects.all()

class AddressRecordDeleteView(AddressRecordView, CommonDeleteView):
    """ """

class AddressRecordDetailView(AddressRecordView, CommonDetailView):
    """ """

class AddressRecordCreateView(AddressRecordView, CreateView):
    template_name = "address_record_update.html"
    def post( self, request, *args, **kwargs ):
        record_form = AddressRecordForm( request.POST )
        ip_form = IpForm( request.POST, instance=Ip() )
        # Attempt to create record.
        try:
            errors = False
            ip_type = request.POST['ip_type']
            record_form.instance.ip_type, ip_form.instance.ip_type = ip_type, ip_type

            record = record_form.save( commit=False )
            ip = ip_form.save()
            ip.save()

            record.ip = ip
            record.save()
        except ValueError, e:
            return render( request, "address_record_create.html", { "record_form": record_form, "ip_form": ip_form, 'ip_type': ip_type } )

        # Success. Redirect.
        messages.success( request, "Successfully Created Record." )
        return redirect( record )

    def get( self, request, *args, **kwargs ):
        record_form = AddressRecordForm()
        ip_form = IpForm()
        return render( request, "address_record_create.html", { "record_form": record_form, "ip_form": ip_form } )

class AddressRecordUpdateView(AddressRecordView, UpdateView):
    template_name = "address_record_update.html"

    def post( self, request, *args, **kwargs ):
        record = get_object_or_404( AddressRecord, pk = kwargs.get('pk', 0) )
        record_form = AddressRecordForm( request.POST, instance=record )
        ip_form = IpForm( request.POST, instance=record.ip )
        try:
            # Updating
            record = record_form.save(commit =False)
            ip = ip_form.save(commit=False)
            record.save()
            ip.save()
        except ValueError, e:
            return render( request, "address_record_update.html", { "record_form": record_form, "ip_form": ip_form } )

        # Success.
        messages.success(request, '%s was successfully updated.' % (record.__str__()))
        return redirect( record )

    def get( self, request, *args, **kwargs ):
        record = get_object_or_404( AddressRecord, pk = kwargs.get('pk', 0) )
        record_form = AddressRecordForm( instance = record )
        ip_form = IpForm( instance = record.ip )
        return render( request, "address_record_update.html", { "record_form": record_form, "ip_form": ip_form } )

