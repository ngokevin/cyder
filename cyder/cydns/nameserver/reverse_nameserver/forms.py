from django import forms
from django.forms import ModelForm

from cyder.cydns.nameserver.reverse_nameserver.models import ReverseNameserver


class ReverseNameserverForm(ModelForm):
    class Meta:
        model = ReverseNameserver
