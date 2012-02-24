from django.forms import ModelForm
from cyder.cydns.mx.models import MX

class MXForm( ModelForm ):
    class Meta:
        model   = MX
