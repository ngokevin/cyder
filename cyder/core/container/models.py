from django.db import models
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import Reverse_Domain
from cyder.cyuser.models import CyUser


class CTNR( models.Model ):
    id              = models.AutoField(primary_key=True)
    ranges          = models.ManyToManyField(Range, null=False)
    domains         = models.ManyToManyField(Domain, null=False)
    reverse_domains = models.ManyToManyField(Reverse_Domain, null=False)
    users           = models.ManyToManyField(CyUser, null=False, related_name='users')
    admins          = models.ManyToManyField(CyUser, null=False)
    description     = models.CharField(max_length=200)
    name            = models.CharField(max_length=100)
    notify          = models.BooleanField()
    purgeable       = models.BooleanField()

    class Meta:
        db_table = 'ctnr'
