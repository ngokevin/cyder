from django.conf import settings
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr, CtnrUser

def has_perm(self, request, obj, write=False):
    """
    Check if user (in request obj) has permission to act on given obj by
    first checking if obj is within current ctnr. If obj in ctnr, permissions
    will then depend on whether the action is read or write and whether user
    has admin over ctnr. Only ctnr admins can do write-related actions.
    Non-admins that are users of a ctnr can only do read-related actions. To be
    full admin (superuser), the user must be admin of the 'global' ctnr (pk=1).
    Full admins have read and write to every obj.

    # ask for write (create, update, delete) permissions to a domain object
    perm = request.user.get_profile().has_perm(request, aDomainObj, write=True)
    """
    # full admins automatically have perms
    if request.user.is_superuser:
        return True
    try:
        if CtnrUser.objects.get(ctnr=1, user=request.user).is_admin:
            return True
    except CtnrUser.DoesNotExist:
        pass

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
        is_admin = CtnrUser.objects.get(ctnr=ctnr, user=request.user).is_admin
    except CtnrUser.DoesNotExist:
        return False

    # cntr admin (can read and write)
    if is_admin:
        return True

    # user (can only read)
    elif not is_admin and not write:
        return True

    return False
