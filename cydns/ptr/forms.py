from django.forms import ModelForm
from cyder.cydns.ptr.models import PTR

class PTRForm( ModelForm ):
    class Meta:
        model   = PTR
