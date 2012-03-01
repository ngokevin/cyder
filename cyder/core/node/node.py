from django.db import models
from cyder.core.container import Container

class Node( models.Model ):
    id              = models.AutoField(primary_key=True)
    ctnr           = models.ForeignKey(Container, null=False)

