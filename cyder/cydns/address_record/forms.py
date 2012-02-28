from django.forms import ModelForm
from cyder.cydns.address_record.models import AddressRecord

class AddressRecordForm( ModelForm ):
    class Meta:
        model   = AddressRecord
        exclude = ('ip',)
