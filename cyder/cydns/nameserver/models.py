from django.db import models
from django.forms import ValidationError
from cyder.settings import CYDNS_BASE_URL
from cyder.cydns.address_record.models import Domain, _check_TLD_condition
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cydns import _validate_label, _validate_name, InvalidRecordNameError, RecordExistsError
import pdb

class Nameserver( models.Model ):
    id              = models.AutoField(primary_key=True)
    domain          = models.ForeignKey(Domain, null=False)
    # "If the name server does lie within the domain it should have a corresponding A record."
    server          = models.CharField(max_length=256)
    glue            = models.ForeignKey(AddressRecord, null=True, blank=True)

    class Meta:
        db_table = 'nameserver'

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Domain', self.domain),
                    ('Server', self.server),
                    ('Glue', self.glue),
                )

    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/nameserver/%s/detail" % (self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/nameserver/%s/update" % (self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/nameserver/%s/delete" % (self.pk)

    def __init__(self, *args, **kwargs):
        super(Nameserver, self).__init__(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Nameserver, self).delete(*args, **kwargs)

    def clean( self ):
        if type(self.server) not in (type(''), type(u'')):
            raise InvalidRecordNameError("Error: name must be type str")

        _validate_name( self.server )
        _check_exist( self )
        _check_TLD_condition( self )

        needs_glue = _needs_glue( self )
        if self.glue and self.glue.fqdn() != self.server:
            if not needs_glue:
                raise NSRecordMisconfiguredError("Error: %s does not need a glue record." % (str(self)))
            else:
                raise NSRecordMisconfiguredError("Error: %s needs a correct glue record." % (str(self)))
        if not self.glue and needs_glue:
            raise NSRecordMisconfiguredError("Error: %s is in the %s domain. It needs a glue record." %\
                    (self.server, self.domain.name))


    def save(self, *args, **kwargs):
        self.clean()
        super(Nameserver, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s" % ( self.domain.name, 'NS', self.server )

    def __repr__(self):
        return "<NS Record '%s'>" % (str(self))


class NSRecordMisconfiguredError(ValidationError):
    """This exception is thrown when an attempt is made to create an NS record that requires a glue, but
       a glue record is not found."""

def _needs_glue( ns ):
    # Replace the domain portion of the server with "".
    # if domain == foo.com and server == ns1.foo.com.
    #       ns1.foo.com --> ns1
    possible_label = ns.server.replace("."+ns.domain.name, "")
    try:
        _validate_label(possible_label)
    except InvalidRecordNameError, e:
        # It's not a valid label
        return False
    return True

def _check_TLD_condition( ns ):
    domain = Domain.objects.filter( name = ns.server )
    if not domain:
        return
    else:
        raise InvalidRecordNameError( "You cannot create a NS record that is the name of a domain." )

def _check_exist( ns ):
    exist = Nameserver.objects.filter( server = ns.server, domain = ns.domain )
    for possible in exist:
        if possible.pk != ns.pk:
            raise RecordExistsError(str(possible)+" already exists.")
