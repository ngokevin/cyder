from django.db import models

from cyder.cydns.common.models import CommonRecord

class TXT(CommonRecord):
    id              = models.AutoField(primary_key=True)
    txt_data        = models.TextField()

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Record Type', 'TXT'),
                    ('Text', self.txt_data)
                )

    class Meta:
        db_table = 'txt'
        #unique_together = ('domain', 'label', 'txt_data')
        # TODO
        # _mysql_exceptions.OperationalError: (1170, "BLOB/TEXT column 'txt_data' used in key specification without a key length")
        # Fix that ^
