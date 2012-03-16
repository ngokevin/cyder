from django.db import models
from django import forms

from cyder.cydns.domain.models import Domain, _check_TLD_condition
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import InvalidRecordNameError, _validate_name
from cyder.cydns.cydns import  _validate_label, _validate_ttl

import pdb

class MX( CommonRecord ):
    id              = models.AutoField(primary_key=True)
    # The mail server this record should point to.
    server          = models.CharField(max_length=100)
    priority        = models.PositiveIntegerField(null=False)
    ttl             = models.PositiveIntegerField(null=False)

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Record Type', 'MX'),
                    ('Server', self.server),
                    ('Priority', self.priority),
                    ('TTL', self.ttl)
                )
    class Meta:
        db_table = 'mx'
        # label and domain in CommonRecord
        unique_together = ('domain', 'label', 'server', 'priority')

    def delete(self, *args, **kwargs):
        super(MX, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(MX, self).save(*args, **kwargs)

    def clean( self ):
        _validate_label( self.label )
        _validate_name( self.server )
        _validate_ttl( self.ttl )
        _check_TLD_condition( self )
        self._validate_mx_priority()

    def __str__(self):
        return "%s %s %s %s %s %s" % ( self.fqdn(), self.ttl, 'IN', 'MX',\
                                        self.priority, self.server)

    def fqdn(self):
        if self.label == '':
            fqdn = self.domain.name
        else:
            fqdn = str(self.label)+"."+self.domain.name
        return fqdn

    def __repr__(self):
        return "<MX '%s'>" % (self.__str__())

    def _validate_mx_priority( self ):
        if self.priority > 65535 or self.priority < 0:
            raise InvalidRecordNameError("Error: MX priority must be within the 0 to 65535\
                                            range. See RFC 1035")
