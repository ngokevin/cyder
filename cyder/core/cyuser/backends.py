from django.conf import settings
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr, CtnrUser


def has_perm(self, request, obj, action):
    """
    Checks whether a user (``request.user``) has permission to act on a
    given object (``obj``) within the current session CTNR. Permissions will
    depend on whether the object is within the user's current CTNR and whether
    the user is admin to that CTNR. If so, they have full permissions to
    objects within their CTNR.  Else, they are only users to the CTNR and have
    only read permissions. Full admins (superusers) have read and write
    permissions on every object in every CTNR. To be a full admins, the user
    must be an admin of the 'global' CTNR (``pk=1``).

    :param request: A django request object.
    :type request: :class:`request`
    :param obj: The object being tested for permission.
    :type obj: :class:`object`
    :param write: The type of permission on the object. ``True`` for
        write, ``False`` for read.
    :type write: Boolean

    An example of checking whether a user has 'write' permission on a
    :class:`Domain` object.
        >>> perm = request.user.get_profile().has_perm(request, domain,
        ... write=True)

    """
    user = request.user
    ctnr = request.session['ctnr']
    obj_type = obj.__class__.__name__

    # enforce obj-ctnr relation to update/delete it even if admin/superadmin
    if (action == 'update' or action == 'delete') \
    and not obj_in_ctnr(obj, ctnr) and obj_type != 'Ctnr':
        return False

    # handle SUPERUSERS
    # superusers automatically get permissions
    if request.user.is_superuser:
        return True

    # handle PLEBS
    # plebs (autoreg students) get no permissions
    elif not CtnrUser.objects.get(user=user):
        return False

    # get level, user is explictly admin, user, or guest
    is_cyder_admin = CtnrUser.objects.get(ctnr=1, user=user).level == 2
    is_ctnr_admin = CtnrUser.objects.get(ctnr=ctnr, user=user).level == 2
    is_admin = is_cyder_admin or is_ctnr_admin

    is_cyder_user = CtnrUser.objects.get(ctnr=1, user=user).level == 1
    is_ctnr_user = CtnrUser.objects.get(ctnr=ctnr, user=user).level == 1
    is_user = (is_cyder_user or is_ctnr_user) and not is_admin

    is_cyder_guest = CtnrUser.objects.get(ctnr=1, user=user).level == 0
    is_ctnr_guest = CtnrUser.objects.get(ctnr=ctnr, user=user).level == 0
    is_guest = (is_cyder_guest or is_ctnr_guest) and not is_admin and not is_user

    # everyone (except plebs) can view everything in their ctnrs
    in_ctnr = is_admin or is_user or is_guest
    if action == 'view' and in_ctnr:
        return True

    # handle ZONE GUESTS
    # zone guests can only view
    elif action != 'view' and is_guest:
        return False

    # handle ctnr objects
    # for ctnrs, let admins only update
    if obj_type == 'Ctnr':
        if is_admin and action == 'update':
            return True
        else:
            return False

    # handle CYDER ADMIN and CTNR ADMIN
    # admins can do everything except create domains, soas, ctnrs
    if (obj_type == 'Domain' or obj_type == 'SOA' or obj_type == 'Ctnr') \
    and action == 'create':
        return False
    elif is_admin:
        return True

    # handle CYDER USERS and CTNR USERS
    if is_user:
        return True
    return False


def obj_in_ctnr(obj, ctnr):
    """
    Checks if an object falls inside a container
    """
    obj_in_ctnr = False
    obj_type = obj.__class__.__name__

    domain_records = [
        'AddressRecord', 'CNAME', 'MX', 'SRV', 'TXT', 'Nameserver'
    ]
    reverse_domain_records = [
        'PTR', 'ReverseNameserver'
    ]

    # domains
    if obj_type == 'Domain':
        domains = ctnr.domains.all()
        if obj in domains:
            obj_in_ctnr = True

    # domain records
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

    # reverse domain records
    elif obj_type in reverse_domain_records:
        reverse_domains = ctnr.reverse_domains.all()
        if obj.reverse_domain in reverse_domains:
            obj_in_ctnr = True

    if not obj_in_ctnr:
        return False
