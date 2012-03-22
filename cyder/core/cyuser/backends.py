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
    if request.user.is_superuser:
        return True

    # first check whether obj falls under the cntr's jurisdiction
    ctnr = request.session['ctnr']

    obj_type = obj._meta.app_label
    obj_in_ctnr = False

    if obj_type == 'domain':
        domains = ctnr.domains.all()
        if obj in domains:
            obj_in_ctnr = True

    if not obj_in_ctnr:
        return False

    # check whether user's level to check if user has perm to do action
    ctnr_user = CtnrUser.objects.get(ctnr=ctnr, user=request.user)
    level = ctnr_user.level

    if level == 10:
        return True

    if perm == 'delete' and level >= 7:
        return True

    if perm == 'create' and level >= 5:
        return True

    if perm == 'update' and level >= 3:
        return True

    if perm == 'view' and level >= 0:
        return True
