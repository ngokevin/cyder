from django.db import models
from cyder.cydhcp.subnet import Subnet

class Subnet_Option( models.Model ):
    #TODO Hard code all options? Stick in option_choices?
    id              = models.AutoField(primary_key=True)
    option          = models.CharField(max_length=500)
    subnet          = models.ManyToMany(Subnet)
