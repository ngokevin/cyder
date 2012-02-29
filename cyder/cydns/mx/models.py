from django.db import models
from django import forms

from cyder.settings.local import CYDNS_BASE_URL
from cyder.cydns.domain.models import Domain
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import InvalidRecordNameError, RecordExistsError, _validate_name, _validate_label, _validate_ttl

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
    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/mx/%s/detail" % (self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/mx/%s/update" % (self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/mx/%s/delete" % (self.pk)

    def delete(self, *args, **kwargs):
        super(MX, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(MX, self).save(*args, **kwargs)

    def clean( self ):
        if type(self.label) not in (str, unicode):
            raise InvalidRecordNameError("Error: name must be type str")
        if type(self.server) not in (str, unicode):
            raise InvalidRecordNameError("Error: name must be type str")
        _validate_label( self.label )
        _validate_name( self.server )
        _validate_mx_priority( self.priority )
        _validate_ttl( self.ttl )
        _check_exists( self )
        _check_TLD_condition( self )

    def __str__(self):
        return "%s %s %s %s %s %s" % ( self.fqdn(), self.ttl, 'IN', 'MX', self.priority, self.server)

    def fqdn(self):
        if self.label == '':
            fqdn = self.domain.name
        else:
            fqdn = str(self.label)+"."+self.domain.name
        return fqdn

    def __repr__(self):
        return "<MX '%s'>" % (self.__str__())

    class Meta:
        db_table = 'mx'


def _validate_mx_priority( prio ):
    if prio > 65535 or prio < 0:
        raise InvalidRecordNameError("Error: MX priority must be within the 0 to 65535 range. See RFC 1035")

def _check_exists( mx ):
    exist = MX.objects.filter( label = mx.label, server = mx.server, priority = mx.priority, ttl = mx.ttl, domain = mx.domain )
    for possible in exist:
        if possible.pk != mx.pk:
            raise RecordExistsError("Error: This MX record already exists.")

def _check_TLD_condition( mx ):
    domain = Domain.objects.filter( name = mx.fqdn() )
    if not domain:
        return
    if mx.label == '' and domain[0] == mx.domain:
        return #This is allowed
    else:
        raise InvalidRecordNameError( "You cannot create a MX record with a non empty label that points to a TLD." )
