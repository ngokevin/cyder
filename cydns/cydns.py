from django.db import models
from cyder.cydns.domain.models import Domain

class CommonRecord(models.Model):
    domain          = models.ForeignKey(Domain, null=False)
    label           = models.CharField(max_length=100)

    class Meta:
        abstract = True
