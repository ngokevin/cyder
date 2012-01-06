from django.db import models
import sys
sys.path.append("/nfs/milo/u1/uberj/cyder")
from cydns.domain import Domain
from cydhcp.subnet import Subnet

class Range( models.Model ):
    RANGE_TYPE_CHOICES = ( ('s','static'),('d','dynamic') )
    id              = models.AutoField(primary_key=True)
    rtype           = models.CharField(max_length=1, choices=RANGE_TYPE_CHOICES)
    start           = models.PositiveIntegerField(null=False)
    end             = models.PositiveIntegerField(null=False)
    default_domain  = models.ForeignKey(Domain, related_name='defualt_domain', null=True)
    subnet          = models.ForeignKey(Domain, null=False)
