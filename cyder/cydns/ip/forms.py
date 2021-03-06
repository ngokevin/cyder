from django import forms
from django.forms import ModelForm
from cyder.cydns.ip.models import Ip

class IpForm( ModelForm ):

    class Meta:
        model   = Ip
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain', )
