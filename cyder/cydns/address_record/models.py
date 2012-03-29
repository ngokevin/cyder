from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.cydns import _validate_label, _validate_name
from cyder.cydns.domain.models import Domain, _check_TLD_condition
from cyder.cydns.ip.models import Ip
from cyder.cydns.common.models import CommonRecord

import pdb

# This is the A and AAAA record class
class AddressRecord( Ip, CommonRecord ):
    """AddressRecord is the class that generates A and AAAA records."""
    id              = models.AutoField(primary_key=True)
    ############################
    # See Ip for all ip fields #
    ############################


    class Meta:
        db_table = 'address_record'
        unique_together = ('label', 'domain', 'ip_str', 'ip_type')

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Record Type', self.record_type()),
                    ('IP', str(self.ip_str)),
                )

    def clean( self ):
        self.clean_ip(update_reverse_domain=False) # Function from Ip class.
        _check_TLD_condition( self )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(AddressRecord, self).save(*args, **kwargs)

    def record_type(self):
        # If PTR didn't share this field, we would use 'A' and 'AAAA' instead of
        # '4' and '6'.
        if self.ip_type == '4':
            return 'A'
        else:
            return 'AAAA'

    def __str__(self):
        return "%s %s %s" % ( self.fqdn(), self.record_type(), str(self.ip_str) )

    def __repr__(self):
        return "<Address Record '%s'>" % (str(self))
