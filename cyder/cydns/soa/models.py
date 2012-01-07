from django.db import models

class Soa( models.Model ):
    id              = models.AutoField(primary_key=True)
    primary         = models.CharField(max_length=100)
    contact         = models.CharField(max_length=100)
    serial          = models.PositiveIntegerField(null=False)
    expire          = models.PositiveIntegerField(null=False)
    retry           = models.PositiveIntegerField(null=False)
    refresh         = models.PositiveIntegerField(null=False)
    class Meta:
        db_table = 'soa'


class SoaNotFoundError(Exception):
    def __str__(self):
        return "No domain found. Condisder creating one."
class SoaExistsError(Exception):
    def __str__(self):
        return "Soa already exists."
