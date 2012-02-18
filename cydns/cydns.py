from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.settings.local import CYDNS_BASE_URL

class CommonRecord(models.Model):
    domain          = models.ForeignKey(Domain, null=False)
    label           = models.CharField(max_length=100, blank=True)
    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/mx/%s/detail" % (self.pk)
    def get_edit_url(self):
        return CYDNS_BASE_URL + "/mx/%s/update" % (self.pk)

    class Meta:
        abstract = True

