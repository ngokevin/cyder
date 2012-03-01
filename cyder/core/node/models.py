from django.db import models
from cyder.core.container.models import Container

class Node( models.Model ):
    id              = models.AutoField(primary_key=True)
    ctnr           = models.ForeignKey(Container, null=False)

    class Meta:
        db_table = 'node'
