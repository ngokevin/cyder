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
    # super-admin
    if request.user.is_superuser:
        return True
    if CtnrUser.objects.get(ctnr=0, user=request.user):
        return True

    # check if obj falls under the cntr
    ctnr = request.session['ctnr']

    obj_type = obj._meta.app_label
    obj_in_ctnr = False

    common_records = ['cname', 'mx', 'txt', 'srv']

    # domains
    if obj_type == 'domain':
        domains = ctnr.domains.all()
        if obj in domains:
            obj_in_ctnr = True

    # soa
    elif obj_type == 'soa':
        domains = ctnr.domains.all()
        soas = [domain.soa for domain in domains]
        if obj in soas:
            obj_in_ctnr = True

    # reverse domains
    elif obj_type == 'reverse_domain':
        reverse_domains = ctnr.reverse_domains.all()
        if obj in reverse_domains:
            obj_in_ctnr = True

    # [cname, mx, txt, srv]
    elif obj_type in common_records:
        domains = ctnr.domains.all()
        if obj.domain in domains:
            obj_in_ctnr = True

    if not obj_in_ctnr:
        return False

    # check user's level to see if user has perm to do action
    ctnr_user = CtnrUser.objects.get(ctnr=ctnr, user=request.user)
    level = ctnr_user.level

    # cntr admin
    if level == 2:
        return True

    if perm == 'delete' and level >= 1:
        return True

    if perm == 'create' and level >= 1:
        return True

    if perm == 'update' and level >= 1:
        return True

    if perm == 'view' and level >= 0:
        return True
