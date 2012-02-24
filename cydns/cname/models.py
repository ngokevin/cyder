from django.db import models
from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.cydns import CommonRecord
from cyder.settings.local import CYDNS_BASE_URL
from cyder.cydns.ip.models import Ip
from cyder.cydns.models import CyAddressValueError, _validate_name, RecordExistsError, RecordNotFoundError, InvalidRecordNameError

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

    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/cname/%s/detail" % (self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/cname/%s/update" % (self.pk)

    class Meta:
        db_table = 'cname'

    def save(self, *args, **kwargs):
        self.clean()
        super(CNAME, self).save(*args, **kwargs)

    def clean( self ):
        if type(self.label) not in (str, unicode):
            raise InvalidRecordNameError("Error: name must be type str")
        _validate_name( self.fqdn() )
        """The RFC for DNS requires that a CName never be at the same level as an SOA, A, or MX
        record. Bind enforces this restriction. When creating a Cname, the UI needs to make sure
        that there are no records of those types that will clash. Likewise, when creating an SOA, A
        or MX, the UI needs to verify that there are no MX records at that level. """
        # TODO ^
        _check_exists( self )
        _check_SOA_condition( self )
        self.data_domain = _name_to_domain( self.data )

    def fqdn( self ):
        if self.label:
            return self.label+"."+self.domain.name
        else:
            return self.domain.name
    def __str__(self):
        return "%s CNAME %s" % (self.fqdn(), self.data)

def _check_exists( cname ):
    exist = CNAME.objects.filter( label = cname.label, domain = cname.domain, data = cname.data )
    for possible in exist:
        if possible.pk != cname.pk:
            raise RecordExistsError( "%s already exists." % (str(possible)))

def _check_SOA_condition( cname ):
    domain = Domain.objects.filter( name = cname.fqdn() )
    if not domain:
        return
    # We need to check if the domain is the root domain in a zone.
    # The domain will have an soa, but the master domain will have no soa (or a different one)
    if domain[0].soa != domain[0].master_domain.soa:
        raise InvalidRecordNameError( "You cannot create a CNAME that points to a domain at the\
                                        root of a zone." )
    return
