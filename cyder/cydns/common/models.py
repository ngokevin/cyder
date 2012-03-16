from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.settings import CYDNS_BASE_URL
from cyder.cydns.models import ObjectUrlMixin

class CommonRecord(models.Model, ObjectUrlMixin):
    domain          = models.ForeignKey(Domain, null=False)
    label           = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True
