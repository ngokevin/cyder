from django.db import models
from cyder.cydhcp.range.models import Range

class Class_Option( models.Model ):
    #TODO Hard code all options? Stick in option_choices?
    id              = models.AutoField(primary_key=True)
    option          = models.CharField(max_length=500)
    ranges           = models.ManyToManyField(Range)

    class Meta:
        db_table = 'class_option'
