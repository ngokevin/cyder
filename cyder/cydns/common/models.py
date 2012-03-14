from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.settings import CYDNS_BASE_URL

class CommonRecord(models.Model):
    domain          = models.ForeignKey(Domain, null=False)
    label           = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/%s/%s/detail" % (self._meta.app_label, self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/%s/%s/update" % (self._meta.app_label, self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/%s/%s/delete" % (self._meta.app_label, self.pk)
