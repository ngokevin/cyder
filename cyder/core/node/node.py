from django.db import models
from cyder.core.container import CTNR

class Node( models.Model ):
    id              = models.AutoField(primary_key=True)
    ctnr           = models.ForeignKey(CTNR, null=False)

