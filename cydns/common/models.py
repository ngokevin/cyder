from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.settings.local import CYDNS_BASE_URL

class CommonRecord(models.Model):
    domain          = models.ForeignKey(Domain, null=False)
    label           = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True
