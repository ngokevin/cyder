from django.contrib.auth.models import User, UserManager
from django.db import models

class CyUser(User):
    """
    Extend Django user model to better support custom authorization backend
    """
    default_ctnr    = models.IntegerField(default=0)
    phone_number    = models.IntegerField(null=True)

    def has_perm(self, request, perm, obj):
        print "YEAH"

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

