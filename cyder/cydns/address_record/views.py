from cyder.cydns.address_record.forms import AddressRecordForm
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.views import CydnsDeleteView, CydnsDetailView
from cyder.cydns.views import CydnsCreateView, CydnsUpdateView, CydnsListView


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


class AddressRecordListView(AddressRecordView, CydnsListView):
    """ """
    template_name = 'address_record/addressrecord_list.html'
