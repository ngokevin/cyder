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

    def fqdn(self):
        if self.label:
            return self.label+"."+self.domain.name
        else:
            return self.domain.name

    class Meta:
        db_table = 'txt'
        #unique_together = ('domain', 'label', 'meta_data')
