from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.common.models import CommonRecord
from cyder.settings import CYDNS_BASE_URL

class TXT( CommonRecord ):
    id              = models.AutoField(primary_key=True)
    meta_data       = models.TextField()

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Record Type', 'TXT'),
                    ('Text', self.meta_data)
                )

    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/txt/%s/detail" % (self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/txt/%s/update" % (self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/txt/%s/delete" % (self.pk)

    def fqdn(self):
        if self.label:
            return self.label+"."+self.domain.name
        else:
            return self.domain.name

    class Meta:
        db_table = 'txt'
