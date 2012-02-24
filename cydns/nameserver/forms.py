from django.forms import ModelForm
from django import forms
from cyder.cydns.nameserver.models import Nameserver

class NameserverForm( ModelForm ):
    class Meta:
        model   = Nameserver
        exclude = ('glue',)
        glue    = forms.CharField(max_length=256, help_text="Enter Glue record if the NS server is \
                                                                within the domain you are assigning the NS server to.")
