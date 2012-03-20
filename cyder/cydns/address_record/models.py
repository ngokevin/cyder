from django.db import models
from django import forms

from cyder.cydns.cydns import _validate_label, InvalidRecordNameError, CyAddressValueError
from cyder.cydns.cydns import _validate_name, RecordExistsError, RecordNotFoundError
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip, ipv6_to_longs
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain
from cyder.settings import CYDNS_BASE_URL

import ipaddr
import string
import pdb

# This is the A and AAAA record class
class AddressRecord( models.Model ):
    """AddressRecord is the class that generates A and AAAA records."""
    IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    id              = models.AutoField(primary_key=True)
    label           = models.CharField(max_length=100)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=False)
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=False)


    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/address_record/%s/detail" % (self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/address_record/%s/update" % (self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/address_record/%s/delete" % (self.pk)

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Record Type', 'A' if self.ip.ip_type == '4' else 'AAAA' ),
                    ('IP', str(self.ip)),
                )

    def __init__(self, *args, **kwargs):
        super(AddressRecord, self).__init__(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.ip.delete()
        super(AddressRecord, self).delete(*args, **kwargs)

    def clean( self ):
        if type(self.label) not in (str, unicode):
            raise InvalidRecordNameError("Error: name must be type str")
        if self.ip_type not in ('4', '6'):
            raise CyAddressValueError("Error: Plase provide the type of Address Record")
        _validate_label( self.label )
        _validate_name( self.fqdn() )
        _check_exist( self )
        _check_TLD_condition( self )

    def save(self, *args, **kwargs):
        self.clean()
        super(AddressRecord, self).save(*args, **kwargs)

    def __str__(self):
        if self.ip_type == '4':
            record_type = 'A'
        else:
            record_type = 'AAAA'
        return "%s %s %s" % ( self.fqdn(), record_type, self.ip.__str__() )

    def fqdn(self):
        if self.label == '':
            fqdn = self.domain.name
        else:
            fqdn = self.label+"."+self.domain.name
        return fqdn

    def __repr__(self):
        return "<Address Record '%s'>" % (self.__str__())

    class Meta:
        db_table = 'address_record'



def _check_exist( record ):
    exist = AddressRecord.objects.filter( label = record.label, domain = record.domain, ip_type = record.ip_type ).select_related('ip')
    for possible in exist:
        if possible.ip.__str__() == record.ip.__str__() and possible.ip.pk != record.ip.pk:
            raise RecordExistsError(possible.__str__()+" already exists.")


def _check_TLD_condition( record ):
    domain = Domain.objects.filter( name = record.fqdn() )
    if not domain:
        return
    if record.label == '' and domain[0] == record.domain:
        return #This is allowed
    else:
        raise InvalidRecordNameError( "You cannot create TLD A record for another domain." )

