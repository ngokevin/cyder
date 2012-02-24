from django.forms import ModelForm
from django import forms
from cyder.cydns.reverse_domain.models import ReverseDomain

class ReverseDomainUpdateForm( ModelForm ):
    class Meta:
        model   = ReverseDomain
        exclude = ('name','master_reverse_domain', 'ip_type')


class ReverseDomainForm( ModelForm ):
    choices = ( (1,'Yes'),
                (0,'No'),
              )
    inherit_soa = forms.ChoiceField(widget=forms.RadioSelect, choices=choices, required=False)
    class Meta:
        model   = ReverseDomain
        exclude = ('master_reverse_domain',)
