from django.db import models
from cyder.cydhcp.group import Group

class Group_Option( models.Model ):
    #TODO Hard code all options? Stick in option_choices?
    id              = models.AutoField(primary_key=True)
    option          = models.CharField(max_length=500)
    group           = models.ManyToMany(Group)
