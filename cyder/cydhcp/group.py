from django.db import models
from cyder.cydns.domain import Domain
from cyder.cydhcp.subnet import Subnet

class Group( models.Model ):
    RANGE_TYPE_CHOICES = ( ('s','static'),('d','dynamic') )
    id              = models.AutoField(primary_key=True)
    rtype           = models.CharField(max_length=1, choices=RANGE_TYPE_CHOICES)
    start           = models.PositiveIntegerField(null=False)
    end             = models.PositiveIntegerField(null=False)
    default_domain  = models.ForeignKey(Domain, null=True)
    subnet          = models.ForeignKey(Domain, null=False)
