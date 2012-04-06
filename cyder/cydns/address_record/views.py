# Create your views here.
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.address_record.forms import AddressRecordForm
from cyder.cydns.common.views import CommonDeleteView, CommonDetailView
from cyder.cydns.common.views import CommonCreateView, CommonUpdateView

import pdb


class AddressRecordView(object):
    model = AddressRecord
    form_class = AddressRecordForm
    queryset = AddressRecord.objects.all()


class AddressRecordDeleteView(AddressRecordView, CommonDeleteView):
    """ """


class AddressRecordDetailView(AddressRecordView, CommonDetailView):
    """ """


class AddressRecordCreateView(AddressRecordView, CommonCreateView):
    """ """


class AddressRecordUpdateView(AddressRecordView, CommonUpdateView):
    """ """
