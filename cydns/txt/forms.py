from django.forms import ModelForm
from cyder.cydns.txt.models import TXT

class TXTForm( ModelForm ):
    class Meta:
        model   = TXT
