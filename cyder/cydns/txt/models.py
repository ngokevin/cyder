from django.db import models
from cyder.cydns.domain.models import Domain

class TXT( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    meta_data       = models.TextField()
    domain          = models.ForeignKey(Domain, null=False)

    class Meta:
        db_table = 'txt'
