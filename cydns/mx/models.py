from django.db import models
from cyder.cydns.domain.models import Domain

class MX( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    server          = models.CharField(max_length=100)
    domain          = models.ForeignKey(Domain, null=False)
    priority        = models.PositiveIntegerField(null=False)
    ttl             = models.PositiveIntegerField(null=False)

    class Meta:
        db_table = 'mx'
