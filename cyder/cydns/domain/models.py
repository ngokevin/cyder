from django.db import models
from cyder.cydns.soa.models import Soa

class Domain( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    master_domain   = models.ForeignKey("self", null=True)
    soa             = models.ForeignKey(Soa, null=True)

    class Meta:
        db_table = 'domain'
