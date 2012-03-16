from django.db import models

from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import CyAddressValueError, _validate_name
from cyder.cydns.cydns import InvalidRecordNameError, _validate_label

class CNAME( CommonRecord ):
    id              = models.AutoField(primary_key=True)
    data            = models.CharField(max_length=100)
    data_domain     = models.ForeignKey(Domain, null=True, related_name = 'data_domains')

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Record Type', 'CNAME'),
                    ('Data', self.data),
                )

    class Meta:
        db_table = 'cname'
        unique_together = ('domain', 'label', 'data')

    def save(self, *args, **kwargs):
        self.clean()
        super(CNAME, self).save(*args, **kwargs)

    def clean( self ):
        _validate_label( self.label )
        _validate_name( self.fqdn() )
        """The RFC for DNS requires that a CName never be at the same level as an SOA, A, or MX
        record. Bind enforces this restriction. When creating a Cname, the UI needs to make sure
        that there are no records of those types that will clash. Likewise, when creating an SOA, A
        or MX, the UI needs to verify that there are no MX records at that level. """
        # TODO ^
        self._check_SOA_condition()
        self.data_domain = _name_to_domain( self.data )

    def fqdn( self ):
        if self.label:
            return self.label+"."+self.domain.name
        else:
            return self.domain.name
    def __str__(self):
        return "%s CNAME %s" % (self.fqdn(), self.data)


    def _check_SOA_condition( self ):
        domain = Domain.objects.filter( name = self.fqdn() )
        if not domain:
            return
        # We need to check if the domain is the root domain in a zone.
        # The domain will have an soa, but the master domain will have no soa (or a different one)

        if domain[0].soa and domain[0].soa != domain[0].master_domain.soa:
            raise InvalidRecordNameError( "You cannot create a CNAME that points to a domain at the\
                                            root of a zone." )
        return
