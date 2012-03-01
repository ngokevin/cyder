from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals

from cyder.core.container.models import CTNR


class UserProfile( models.Model ):
    user            = models.OneToOneField(User)
    default_ctnr    = models.ForeignKey(CTNR, null=True)
    phone_number    = models.IntegerField(null=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

signals.post_save.connect(create_user_profile, sender=User)
