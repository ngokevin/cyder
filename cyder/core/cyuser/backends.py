from django.conf import settings
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr, CtnrUser

def has_perm(self, request, obj, write=False):
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
