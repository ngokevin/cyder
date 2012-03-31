from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.cydns import _validate_label, _validate_name
from cyder.cydns.domain.models import Domain, _check_TLD_condition
from cyder.cydns.ip.models import Ip
from cyder.cydns.common.models import CommonRecord

import pdb

# This is the A and AAAA record class
class AddressRecord( Ip, CommonRecord ):
    """
    AddressRecord is the class that generates A and AAAA records::

        AddressRecord(label=label, domain=domain_object, ip_str=ip_str, ip_type=ip_type)

    """
    id              = models.AutoField(primary_key=True)
    ############################
    # See Ip for all ip fields #
    ############################


    class Meta:
        db_table = 'address_record'
        unique_together = ('label', 'domain', 'ip_str', 'ip_type')

    def details(self):
        return  (
                    ('FQDN', self.fqdn),
                    ('Record Type', self.record_type()),
                    ('IP', str(self.ip_str)),
                )

    #def __setattr__(self, *args, **kwargs):

    def clean( self ):
        self._check_glue_status()
        super(AddressRecord, self).clean()
        super(AddressRecord, self).check_for_delegation()
        self.clean_ip(update_reverse_domain=False) # Function from Ip class.
        _check_TLD_condition( self )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(AddressRecord, self).save(*args, **kwargs)

    def _check_glue_status(self):
        """
        If this record is a 'glue' record for a Nameserver instance, do not allow modifications to
        this record. The Nameserver will need to point to a different record before this record can
        be updated.
        """
        if self.pk is None:
            return
        # First get this object from the database and compare it to the object about to be saved.
        db_self = AddressRecord.objects.get(pk=self.pk)
        if db_self.label == self.label and db_self.domain == self.domain:
            return
        # The label of the domain changed. Make sure it's not a glue record
        from cyder.cydns.nameserver.models import Nameserver # This avoids cyclic imports
        if Nameserver.objects.filter(glue=self).exists():
            raise ValidationError("This record is a glue record for a Nameserver. Change the\
                    Nameserver to edit this record.")

    def record_type(self):
        # If PTR didn't share this field, we would use 'A' and 'AAAA' instead of
        # '4' and '6'.
        if self.ip_type == '4':
            return 'A'
        else:
            return 'AAAA'

    def __str__(self):
        return "%s %s %s" % ( self.fqdn, self.record_type(), str(self.ip_str) )

    def __repr__(self):
        return "<Address Record '%s'>" % (str(self))
