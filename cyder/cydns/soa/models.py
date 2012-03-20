from django.db import models

from cyder.cydns.cydns import _validate_name
from cyder.cydns.models import ObjectUrlMixin

import time
import pdb

#TODO, put these defaults in a config file.
ONE_WEEK = 604800
DEFAULT_EXPIRE = ONE_WEEK*2
DEFAULT_RETRY = ONE_WEEK/7 # One day
DEFAULT_REFRESH = 180 # 3 min

class SOA(models.Model, ObjectUrlMixin):
    id              = models.AutoField(primary_key=True)
    primary         = models.CharField(max_length=100, validators=[_validate_name])
    contact         = models.CharField(max_length=100, validators=[_validate_name])
    serial          = models.PositiveIntegerField(null=False)
    # Indicates when the zone data is no longer authoritative. Used by slave.
    expire          = models.PositiveIntegerField(null=False, default = DEFAULT_EXPIRE)
    # The time between retries if a slave fails to contact the master when refresh (below) has expired.
    retry           = models.PositiveIntegerField(null=False, default = DEFAULT_RETRY)
    # The time when the slave will try to refresh the zone from the master
    refresh         = models.PositiveIntegerField(null=False, default = DEFAULT_REFRESH)
    # This indicates if this zone needs to be rebuilt
    dirty           = models.BooleanField(default = False)

    class Meta:
        db_table = 'soa'
        unique_together = ('primary', 'contact')

    def details(self):
        return  (
                    ('Primary', self.primary),
                    ('Contact', self.contact),
                    ('Serial', self.serial),
                    ('Expire', self.expire),
                    ('Retry', self.retry),
                    ('Refresh', self.refresh),
                )

    def delete(self, *args, **kwargs):
        super(SOA, self).delete(*args, **kwargs)


    def save(self, *args, **kwargs):
        self.serial = int(time.time())
        self.full_clean()
        super(SOA, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % ('SOA', str(self.primary))

    def __repr__(self):
        return "<'%s'>" % (str(self))

