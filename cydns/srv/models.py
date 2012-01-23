from django.db import models
from cyder.cydns.domain.models import Domain

class SRV( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    target          = models.CharField(max_length=100)
    domain          = models.ForeignKey(Domain, null=False)
    priority        = models.PositiveIntegerField(null=False)
    weight          = models.PositiveIntegerField(null=False)

    class Meta:
        db_table = 'srv'
