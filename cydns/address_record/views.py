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

from cyder.cydns.address_record.models import AddressRecord, AddressRecordForm
from cyder.cydns.ip.models import Ip, IpForm

import pdb

@csrf_exempt
def address_record_create(request):
    if request.method == 'POST':
        record_form = AddressRecordForm( request.POST, instance=AddressRecord() )
        ip_form     = IpForm( request.POST, instance=Ip() )
        # Attempt to create record.
        try:
            errors = False
            ip_type = request.POST['ip_type']
            record_form.instance.ip_type, ip_form.instance.ip_type = ip_type, ip_type
            try:
                record = record_form.save( commit=False )
            except Exception, e:
                messages.error( request, e.__str__() )
                errors = True
            try:
                ip     = ip_form.save()
            except Exception, e:
                messages.error( request, e.__str__() )
                errors = True

            if errors: raise Exception

            record.ip = ip
            record.save()
        except Exception, e:
            return render( request, "address_record_create.html", { "record_form": record_form, "ip_form": ip_form, 'ip_type': ip_type } )

        # Success. Redirect.
        messages.success(request, '%s was successfully added.' % (record.__str__()))
        return redirect('cyder.cydns.address_record.views.address_record_update', pk = record.pk )
    else:
        record_form = AddressRecordForm()
        ip_form     = IpForm()
        return render( request, "address_record_create.html", { "record_form": record_form, "ip_form": ip_form } )


@csrf_exempt
def address_record_update(request, pk):
    record = AddressRecord.objects.get( pk = pk )
    if request.method == 'POST':
        record_form = AddressRecordForm( request.POST, instance=record )
        ip_form     = IpForm( request.POST, instance=record.ip )
        try:
            if record_form.data.get('delete', False ):
                info        = record.__str__()
                domain_pk   = record.domain.pk
                record.delete()
                messages.success(request, '%s was successfully deleted.' % (info))
                return redirect('/cyder/cydns/domain/%s/update' % (domain_pk) )
            record = record_form.save(commit=False)
            ip     = ip_form.save(commit=False)
            record.save()
            ip.save()
        except Exception, e:
            messages.error( request, e.__str__() )
            return render( request, "address_record_update.html", { "record_form": record_form, "ip_form": ip_form } )

        # Success.
        messages.success(request, '%s was successfully updated.' % (record.__str__()))
        return render( request, "address_record_update.html", { "record_form": record_form, "ip_form": ip_form } )
    else:
        record_form = AddressRecordForm( instance=record )
        ip_form     = IpForm( instance=record.ip )
        return render( request, "address_record_update.html", { "record_form": record_form, "ip_form": ip_form } )

