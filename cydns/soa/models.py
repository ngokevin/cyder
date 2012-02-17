from django.db import models
from cyder.settings.local import CYDNS_BASE_URL
from cyder.cydns.models import _validate_name, CyAddressValueError, InvalidRecordNameError
from cyder.cydns.models import RecordExistsError, RecordNotFoundError
from django.forms import ModelForm
from django import forms
import time
import pdb

ONE_WEEK = 604800
DEFAULT_EXPIRE = ONE_WEEK*2
DEFAULT_RETRY = ONE_WEEK/7 # One day
DEFAULT_REFRESH = 180 # 3 min

class SOA( models.Model ):
    id              = models.AutoField(primary_key=True)
    primary         = models.CharField(max_length=100)
    contact         = models.CharField(max_length=100)
    serial          = models.PositiveIntegerField(null=False)
    # Indicates when the zone data is no longer authoritative. Used by slave.
    expire          = models.PositiveIntegerField(null=False, default = DEFAULT_EXPIRE)
    # The time between retries if a slave fails to contact the master when refresh (below) has expired.
    retry           = models.PositiveIntegerField(null=False, default = DEFAULT_RETRY)
    # The time when the slave will try to refresh the zone from the master
    refresh         = models.PositiveIntegerField(null=False, default = DEFAULT_REFRESH)
    # This indicates if this zone needs to be rebuilt
    dirty           = models.BooleanField( default = False )
    class Meta:
        db_table = 'soa'

    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/soa/%s/detail" % (self.pk)

    def delete(self, *args, **kwargs):
        super(SOA, self).delete(*args, **kwargs)

    def clean( self ):
        _validate_name( self.primary )
        _validate_name( self.contact )

    def save(self, *args, **kwargs):
        self.serial = int(time.time())
        self.clean()
        super(SOA, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s" % ( self.primary.__str__(), 'SOA', self.serial )

    def __repr__(self):
        return "<SOA Record '%s'>" % (self.__str__())

class SOAForm( ModelForm ):
    class Meta:
        model   = SOA
        exclude = ('serial','dirty',)
