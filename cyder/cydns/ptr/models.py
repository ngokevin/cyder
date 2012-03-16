from django.db import models

from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.ip.models import Ip
from cyder.cydns.cydns import _validate_name, RecordExistsError
from cyder.cydns.cydns import InvalidRecordNameError
from cyder.cydns.models import ObjectUrlMixin

class PTR( models.Model, ObjectUrlMixin ):
    """A PTR is used to map an IP to a domain name"""
    IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=False)
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=255)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=True)

    def details(self):
        return  (
                    ('Ip', str(self.ip)),
                    ('Record Type', 'PTR'),
                    ('Name', self.name),
                )
    class Meta:
        db_table = 'ptr'

    def delete(self, *args, **kwargs):
        self.ip.delete()
        super(PTR, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(PTR, self).save(*args, **kwargs)

    def clean( self ):
        _validate_name( self.name )
        self.validate_unique()
        self.domain = _name_to_domain( self.name )

    def __str__(self):
        return "%s %s %s" % (str(self.ip), 'PTR', self.name )
    def __repr__(self):
        return "<%s>" % (str(self))


    def validate_unique( self, *args, **kwargs ):
        exist = PTR.objects.filter( name = self.name ).select_related('ip')
        for possible in exist:
            if possible.ip.pk != self.ip.pk and str(possible.ip).lower() == str(self.ip).lower():
                raise RecordExistsError( "%s already exists." % (str(possible)) )
