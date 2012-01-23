from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip

class PTR( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=False)

    class Meta:
        db_table = 'ptr'
