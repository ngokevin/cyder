from django.db import models
from django.core.exceptions import ValidationError


from cyder.cydns.cydns import _validate_label, InvalidRecordNameError, CyAddressValueError
from cyder.cydns.cydns import _validate_name, RecordExistsError
from cyder.cydns.domain.models import Domain, _check_TLD_condition
from cyder.cydns.ip.models import Ip
from cyder.cydns.models import ObjectUrlMixin

import pdb

# This is the A and AAAA record class
class AddressRecord( models.Model, ObjectUrlMixin ):
    """AddressRecord is the class that generates A and AAAA records."""
    IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    id              = models.AutoField(primary_key=True)
    label           = models.CharField(max_length=100)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=False)
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=False)


    class Meta:
        db_table = 'address_record'

    def validate_unique( self, *args, **kwargs ):
        """You can't do unique constraints across a foriegn key using 'unique_together'.
        We need the ip to not be the same so we have a validate_unique function.
        RecordExistsError is a subclass of ValidationError.
        note::
            https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.validate_unique
        """
        exist = AddressRecord.objects.filter( label = self.label, domain = self.domain,\
                                            ip_type = self.ip_type ).select_related('ip')
        for possible in exist:
            if str(possible.ip) == str(self.ip) and possible.ip.pk != self.ip.pk:
                raise RecordExistsError(str(self)+" already exists.")

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
        if self.ip_type not in ('4', '6'):
            raise CyAddressValueError("Error: Plase provide the type of Address Record")
        _validate_label( self.label )
        _validate_name( self.fqdn() )
        self.validate_unique()
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

    def __repr__(self):
        return "<Address Record '%s'>" % (self.__str__())

    def fqdn(self):
        if self.label == '':
            fqdn = self.domain.name
        else:
            fqdn = self.label+"."+self.domain.name
        return fqdn

