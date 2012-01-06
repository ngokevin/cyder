from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import Address_Record

class Nameserver( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    glue            = models.ForeignKey(Address_Record, null=False)
    domain          = models.ForeignKey(Domain, null=False)

    class Meta:
        db_table = 'nameserver'
