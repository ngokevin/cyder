from django.db import models
from cyder.dhcp.range import Range
from cyder.dns.domain import Domain
from cyder.dns.reverse_domain import ReverseDomain
from cyder.user import CyUser


class CTNR( models.Model ):
    id              = models.AutoField(primary_key=True)
    ranges          = models.ManyToManyField(Range, null=False)
    domains         = models.ManyToManyField(Domain, null=False)
    reverse_domains = models.ManyToManyField(ReverseDomain, null=False)
    users           = models.ManyToManyField(CyUser, null=False)
    admins          = models.ManyToManyField(CyUser, null=False)
