from django.forms import ModelForm
from cyder.cydns.cname.models import CNAME

class CNAMEForm( ModelForm ):
    class Meta:
        model   = CNAME
        exclude = ('data_domain', )
