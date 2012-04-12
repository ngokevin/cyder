from django.db import models
from cyder.cydhcp.group.models import Group

class Group_Option( models.Model ):
    #TODO Hard code all options? Stick in option_choices?
    id              = models.AutoField(primary_key=True)
    option          = models.CharField(max_length=500)
    groups           = models.ManyToManyField(Group)

    class Meta:
        db_table = 'group_option'
