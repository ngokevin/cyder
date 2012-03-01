from django.db import models
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from django.contrib.auth.models import User


class Container( models.Model ):
    id              = models.AutoField(primary_key=True)
    ranges          = models.ManyToManyField(Range, null=False)
    domains         = models.ManyToManyField(Domain, null=False)
    reverse_domains = models.ManyToManyField(ReverseDomain, null=False)
    users           = models.ManyToManyField(User, null=False, related_name='users', through='ContainerUser')
    admins          = models.ManyToManyField(User, null=False, related_name='admins')
    description     = models.CharField(max_length=200)
    name            = models.CharField(max_length=100)
    notify          = models.BooleanField()
    purgeable       = models.BooleanField()

    class Meta:
        db_table = 'container'


class ContainerUser(models.Model):
    user            = models.ForeignKey(User)
    container       = models.ForeignKey(Container)
    level           = models.IntegerField()

    class Meta:
        db_table = 'container_users'
