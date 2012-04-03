from django.conf import settings
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr, CtnrUser

def has_perm(self, request, obj, write=False):
    """
    Check if user has permission to act on given object,
    with the action noted in perm, based on the current container
    whether the object is in that container, and whether user
    has admin over container.
    """
    # super-admin
    if request.user.is_superuser:
        return True

    # check if obj falls under the cntr
    ctnr = request.session['ctnr']

    obj_type = obj.__class__.__name__
    obj_in_ctnr = False

    domain_records = ['CNAME', 'MX', 'TXT', 'SRV', 'AddressRecord',
        'Nameserver']

    reverse_domain_records = ['PTR', 'ReverseNameserver']

    # domains
    if obj_type == 'Domain':
        domains = ctnr.domains.all()
        if obj in domains:
            obj_in_ctnr = True

    # [cname, mx, txt, srv]
    elif obj_type in domain_records:
        domains = ctnr.domains.all()
        if obj.domain in domains:
            obj_in_ctnr = True

    # soa
    elif obj_type == 'SOA':
        domains = ctnr.domains.all()
        soas = [domain.soa for domain in domains]
        if obj in soas:
            obj_in_ctnr = True

    # reverse domains
    elif obj_type == 'ReverseDomain':
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

    # check if user has admin over ctnr
    try:
        global_is_admin = CtnrUser.objects.get(ctnr=1, user=request.user).is_admin
    except CtnrUser.DoesNotExist:
        global_is_admin = False

    try:
        ctnr_is_admin = CtnrUser.objects.get(ctnr=ctnr, user=request.user).is_admin
    except CtnrUser.DoesNotExist:
        if not global_is_admin:
            return False

    # if admin over global ctnr, admin over all ctnr
    is_admin = False
    if global_is_admin or ctnr_is_admin:
        is_admin = True

    # cntr admin
    if is_admin:
        return True

    # user
    elif not is_admin and not write:
        return True

    return False
