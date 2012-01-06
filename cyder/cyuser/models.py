from django.db import models

class CyUser( models.Model ):
    id              = models.AutoField(primary_key=True)
    user_name       = models.CharField(max_length=12)
    email           = models.CharField(max_length=100)

    class Meta:
        db_table = 'user'
