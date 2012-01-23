from django.db import models
from cyder.dns.a_record import A_Record
from cyder.dns.ptr import PTR
from cyder.dhcp.range import Range
from cyder.core.container import CTNR
from cyder.core.node import Node

class Static_Registration( models.Model ):
    id              = models.AutoField(primary_key=True)
    A               = models.OneToOneField(A_Record)
    PTR             = models.OneToOneField(PTR_Record)
    range           = models.ForeignKey(Range, null=False)
    mac             = models.CharField(max_length=12) # TODO make a mac table?
    node            = models.ForeignKey(Node, null=False)

class Dynamic_Registration( models.Model ):
    id              = models.AutoField(primary_key=True)
    range           = models.ForeignKey(Range, null=False)
    mac             = models.CharField(max_length=12) # TODO make a mac table?
    CTNR            = models.ForeignKey(CTNR, null=False)
