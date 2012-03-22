from django.conf import settings
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr, CtnrUser


def has_perm(self, request, perm, obj):
    """
    Check if user has permission to act on given object,
    with the action noted in perm, based on the current container
    whether the object is in that container, and whether user
    has sufficient level.
    """
    container_user = CtnrUser.objects.get(ctnr=request.session['ctnr'], user=request.user)

