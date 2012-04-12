from django.db import models
from cyder.cydhcp.subnet.models import Subnet

class Subnet_Option( models.Model ):
    #TODO Hard code all options? Stick in option_choices?
    id              = models.AutoField(primary_key=True)
    option          = models.CharField(max_length=500)
    subnets          = models.ManyToManyField(Subnet)

    class Meta:
        db_table = 'subnet_option'
