from cyder.cydns.srv.models import SRV
from django.forms import ModelForm


class SRVForm( ModelForm ):
    class Meta:
        model   = SRV
