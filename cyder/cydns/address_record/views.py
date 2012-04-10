# Create your views here.
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.address_record.forms import AddressRecordForm
from cyder.cydns.views import CydnsDeleteView, CydnsDetailView
from cyder.cydns.views import CydnsCreateView, CydnsUpdateView

import pdb


class AddressRecordView(object):
    model = AddressRecord
    form_class = AddressRecordForm
    queryset = AddressRecord.objects.all()


class AddressRecordDeleteView(AddressRecordView, CydnsDeleteView):
    """ """


class AddressRecordDetailView(AddressRecordView, CydnsDetailView):
    """ """
    template_name = 'address_record/addressrecord_detail.html'


class AddressRecordCreateView(AddressRecordView, CydnsCreateView):
    """ """


class AddressRecordUpdateView(AddressRecordView, CydnsUpdateView):
    """ """
