from django.forms import ModelForm
from cyder.cydns.ip.models import Ip

class IpForm( ModelForm ):
    class Meta:
        model   = Ip
        include = ('ip_str','ip_type',)
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain', )
