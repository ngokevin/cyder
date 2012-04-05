from django.contrib.auth.models import User
from django.db import models

from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain


class Ctnr( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    ranges          = models.ManyToManyField(Range, null=False)
    domains         = models.ManyToManyField(Domain, null=False)
    reverse_domains = models.ManyToManyField(ReverseDomain, null=False)
    users           = models.ManyToManyField(User, null=False, related_name='users', through='CtnrUser')
    admins          = models.ManyToManyField(User, null=False, related_name='admins')
    description     = models.CharField(max_length=200)
    purgeable       = models.BooleanField()

    class Meta:
        db_table = 'ctnr'
        unique_together = ('name')


class CtnrUser(models.Model):
    user = models.ForeignKey(User)
    ctnr = models.ForeignKey(Ctnr)
    is_admin = models.IntegerField()

    class Meta:
        db_table = 'ctnr_users'
