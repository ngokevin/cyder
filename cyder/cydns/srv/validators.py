from django.core.exceptions import ValidationError
from cyder.cydns.cydns import _validate_label, _validate_name

def _validate_srv_port(port):
    if port > 65535 or port < 0:
        raise ValidationError("Error: SRV port must be within the 0 to 65535 range. See RFC 1035")

#TODO, is this a duplicate of MX ttl?
def _validate_srv_priority(priority):
    if priority > 65535 or priority < 0:
        raise ValidationError("Error: SRV priority must be within the 0 to 65535 range. See RFC 1035")

def _validate_srv_weight(weight):
    if weight > 65535 or weight < 0:
        raise ValidationError("Error: SRV priority must be within the 0 to 65535 range. See RFC 1035")

def _validate_srv_label(srv_label):
    if srv_label and srv_label[0] != '_':
        raise ValidationError("Error: SRV label must start with '_'")
    _validate_label(srv_label[1:]) # Get rid of '_'

def _validate_srv_name(srv_name):
    if srv_name and srv_name[0] != '_':
        raise ValidationError("Error: SRV label must start with '_'")
    if not srv_name:
        raise ValidationError("Error: SRV label must not be None")
    mod_srv_name = srv_name[1:] # Get rid of '_'
    _validate_name(mod_srv_name)
