from django.db import models

class Subnet( models.Model ):
    SUBNET_STATUS_CHOICES = ( ('v','visible'),('h','hidden') )
    id              = models.AutoField(primary_key=True)
    netmask         = models.PositiveIntegerField(null=False)
    network         = models.PositiveIntegerField(null=False)
    vlan            = models.PositiveIntegerField(null=False)
    status          = models.CharField(max_length=1, choices=SUBNET_STATUS_CHOICES)

    class Meta:
        db_table = 'subnet'
