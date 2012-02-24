from django.db import models
from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.reverse_domain.models import ip_to_reverse_domain, ReverseDomainNotFoundError
from cyder.cydns.ip.models import Ip, ipv6_to_longs
from cyder.cydns.models import CyAddressValueError, _validate_name, RecordExistsError, RecordNotFoundError, InvalidRecordNameError
import ipaddr

class PTR( models.Model ):
    """A PTR is used to map an IP to a domain name"""
    IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=False)
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=256)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=True)


    def delete(self, *args, **kwargs):
        self.ip.delete()
        super(PTR, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(PTR, self).save(*args, **kwargs)

    def clean( self ):
        if type(self.name) not in (type(''), type(u'')):
            raise InvalidRecordNameError("Error: name must be type str")
        _validate_name( self.name )

        _check_exists( self )
        self.domain = _name_to_domain( self.name )

    class Meta:
        db_table = 'ptr'

    def __str__(self):
        return "<Pointer '%s %s %s'>" % (self.ip.__str__(), 'PTR', self.name )
    def __repr__(self):
        return  self.__str__()

def _check_exists( ptr ):
    exist = PTR.objects.filter( name = ptr.name ).select_related('ip')
    for possible in exist:
        if possible.ip.pk != ptr.ip.pk and str(possible.ip).lower() == str(ptr.ip).lower() :
            raise RecordExistsError( "%s already exists." % (str(possible)) )
