from django.db import models
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR
from cyder.cydhcp.range.models import Range
from cyder.core.container.models import CTNR
from cyder.core.node.models import Node

class StaticRegistration( models.Model ):
    id              = models.AutoField(primary_key=True)
    A               = models.OneToOneField(AddressRecord)
    PTR             = models.OneToOneField(PTR)
    range           = models.ForeignKey(Range, null=False)
    mac             = models.CharField(max_length=12) # TODO make a mac table?
    node            = models.ForeignKey(Node, null=False)

    class Meta:
        db_table = 'static_registration'

class DynamicRegistration( models.Model ):
    id              = models.AutoField(primary_key=True)
    range           = models.ForeignKey(Range, null=False)
    mac             = models.CharField(max_length=12) # TODO make a mac table?
    CTNR            = models.ForeignKey(CTNR, null=False)

    class Meta:
        db_table = 'dynamic_registration'
