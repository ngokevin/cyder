from django.db import models
from cyder.cydns.models import _validate_name, CyAddressValueError, InvalidRecordNameError
from cyder.cydns.models import RecordExistsError, RecordNotFoundError
import time
import pdb

class SOA( models.Model ):
    id              = models.AutoField(primary_key=True)
    primary         = models.CharField(max_length=100)
    contact         = models.CharField(max_length=100)
    serial          = models.PositiveIntegerField(null=False)
    expire          = models.PositiveIntegerField(null=False)
    retry           = models.PositiveIntegerField(null=False)
    refresh         = models.PositiveIntegerField(null=False)
    class Meta:
        db_table = 'soa'

# Need to think about how to do this.
DEFAULT_SERIAL = 0

def add_soa( primary, contact, retry, refresh ):
    """Add an SOA record to the database.

        :param  primary: The priary NS for the zone the SOA is being assigned to.
        :type   primary: str. A valid DNS name.
        :param  contact: contact info for the zone.
        :type   contact: str
        :param  retry: Retry interval
        :type   retry: int
        :param  retry: Refresh interval
        :type   retry: int
        :rases: InvalidRecordNameError, RecordExistsError
    """

def remove_soa( soa ):
    """Remove SOA record.
        :param  soa: SOA to be deleted.
        :type   soa: SOA object
    """
    # Go though and set all domains with SOA as their soa, to domain.soa = None

def update_soa( soa, contact=None, serial=None, expire=None, retry=None, refresh=None, ):
    """Update SOA record.
        :param  soa: SOA to be updated.
        :type   soa: SOA object
    """
