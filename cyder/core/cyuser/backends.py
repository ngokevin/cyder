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

    # check if obj falls under the cntr
    ctnr = request.session['ctnr']

    obj_type = obj._meta.app_label
    obj_in_ctnr = False

    domain_records = ['cname', 'mx', 'txt', 'srv', 'address_record',
        'name_server']

    reverse_domain_records = ['ptr', 'reverse_nameserver']

    # domains
    if obj_type == 'domain':
        domains = ctnr.domains.all()
        if obj in domains:
            obj_in_ctnr = True

    # [cname, mx, txt, srv]
    elif obj_type in domain_records:
        domains = ctnr.domains.all()
        if obj.domain in domains:
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

    # [ptr, reverse_nameserver]
    elif obj_type in reverse_domain_records:
        reverse_domains = ctnr.reverse_domains.all()
        if obj.reverse_domain in reverse_domains:
            obj_in_ctnr = True

    if not obj_in_ctnr:
        return False

    # check user's level to see if user has perm to do action
    ctnr_level = CtnrUser.objects.get(ctnr=ctnr, user=request.user)
    global_level = CtnrUser.objects.get(ctnr=0, user=request.user) or -1

    # global ctnr level overrides if higher
    level = ctnr_level
    if global_level > ctnr_level:
        level = global_level

    # cntr admin
    if level == 1:
        return True

    # user
    elif perm == 'view' and level == 0:
        return True

    return False
