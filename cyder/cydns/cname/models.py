from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip

class CNAME( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    data            = models.CharField(max_length=100)
    domain          = models.ForeignKey(Domain, null=False)

    class Meta:
        db_table = 'cname'
