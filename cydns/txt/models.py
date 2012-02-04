from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.cydns import CommonRecord

class TXT( CommonRecord ):
    id              = models.AutoField(primary_key=True)
    meta_data       = models.TextField()

    class Meta:
        db_table = 'txt'
