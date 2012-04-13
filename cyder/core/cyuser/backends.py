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
    :param action: ``view``, ``create, ``update``, ``delete``
    :type action: :class: `string`

    An example of checking whether a user has 'create' permission on a
    :class:`Domain` object.
        >>> perm = request.user.get_profile().has_perm(request, domain,
        ... \'create\')

    """
    # get user level
    user_level = None
    user = request.user
    ctnr = request.session['ctnr']
    is_cyder_admin = CtnrUser.objects.get(ctnr=1, user=user).level == 2
    is_ctnr_admin = CtnrUser.objects.get(ctnr=ctnr, user=user).level == 2
    is_cyder_user = CtnrUser.objects.get(ctnr=1, user=user).level == 1
    is_ctnr_user = CtnrUser.objects.get(ctnr=ctnr, user=user).level == 1
    is_cyder_guest = CtnrUser.objects.get(ctnr=1, user=user).level == 0
    is_ctnr_guest = CtnrUser.objects.get(ctnr=ctnr, user=user).level == 0

    if request.user.superuser:
        return True
    elif is_cyder_admin or is_ctnr_admin:
        user_level = 'cyder_admin'
    elif is_ctnr_admin:
        user_level = 'ctnr_admin'
    elif is_cyder_user or is_ctnr_user:
        user_level = 'user'
    elif is_cyder_guest or is_ctnr_guest:
        user_level = 'guest'
    else:
        user_level = 'pleb'

    # dispatch to appropriate permissions handler
    obj_type = obj.__class__.__name__
    handling_function = {
        # administrative
        'Ctnr': has_administrative_perm,
        'User': has_administrative_perm,

        'SOA': has_soa_perm,

        # top-level ctnr objects
        'Domain': has_domain_perm,
        'ReverseDomain': has_reverse_domain_perm,

        # domain records
        'AddressRecord': has_domain_record_perm,
        'CNAME': has_domain_record_perm,
        'MX': has_domain_record_perm,
        'TXT': has_domain_record_perm,
        'SRV': has_domain_record_perm,
        'Nameserver': has_domain_record_perm,

        # reverse domain records
        'PTR': has_reverse_domain_record_perm,
        'ReverseNameserver': has_reverse_domain_record_perm,

        # dhcp
        'Subnet': has_subnet_perm,
        'Range': has_range_perm,
        'Group': has_group_perm,
        'Node': has_node_perm,

        # options
        'SubnetOption': has_dhcp_option_perm,
        'ClassOption': has_dhcp_option_perm,
        'PoolOption': has_dhcp_option_perm,
        'GroupOption': has_dhcp_option_perm,
    }.get(obj_type, False)
    return handling_function(user_type, action, ctnr, obj)


def has_administrative_perm(user_type, action, obj, ctnr):
    """
    Permissions for ctnrs or users
    Not related to DNS or DHCP objects
    """
    return {
        'cyder_admin': action == 'view' or action =='update',
        'admin': action == 'view' or action =='update',
        'user': action == 'view',
        'guest': action == 'view',
    }.get(user_type, False)


def has_soa_perm(user_type, action, obj, ctnr):
    """
    Permissions for SOAs
    SOAs are global, related to domains and reverse domains
    """
    return {
        'cyder_admin': action == 'view' or action =='update', #?
        'ctnr_admin': action == 'view',
        'user': action == 'view',
        'guest': action == 'view',
    }.get(user_type, False)


def has_domain_perm(user_type, action, obj, ctnr):
    """
    Permissions for domains
    Ctnrs have domains
    """
    if not obj in ctnr.domains.all():
        return False

    return {
        'cyder_admin': action == 'view' or action =='update', #?
        'ctnr_admin': action == 'view' or action == 'update',
        'user': action == 'view' or action == 'update',
        'guest': action == 'view',
    }.get(user_type, False)


def has_reverse_domain_perm(user_type, action, obj, ctnr):
    """
    Permissions for reverse domains
    Ctnrs have reverse domains
    """
    if not obj in ctnr.reverse_domains.all():
        return False

    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == 'view',
    }.get(user_type, False)


def has_domain_record_perm(user_type, action, obj, ctnr):
    """
    Permissions for domain records (or objects linked to a domain)
    Domain records are assigned a domain
    """
    if obj.domain not in ctnr.domains.all():
        return False

    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == 'view',
    }.get(user_type, False)


def has_reverse_domain_record_perm(user_type, action, obj, ctnr):
    """
    Permissions for reverse domain records (or objects linked to a reverse domain)
    Reverse domain records are assigned a reverse domain
    """
    if obj.reverse_domain not in ctnr.reverse_domains.all():
        return False

    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == 'view',
    }.get(user_type, False)


def has_subnet_perm(user_type, action, obj, ctnr):
    """
    Permissions for subnet
    Ranges have subnets
    """
    if not obj in [ip_range.subnet for ip_range in ctnr.ranges.all()]:
        return False

    return {
        'cyder_admin': True, #?
        'ctnr_admin': action == 'view',
        'user': action == 'view',
        'guest': action == 'view',
    }.get(user_type, False)


def has_range_perm(user_type, action, obj, ctnr):
    """
    Permissions for ranges
    Ctnrs have ranges
    """
    if not obj in ctnr.ranges.all():
        return False

    return {
        'cyder_admin': True, #?
        'ctnr_admin': action == 'view',
        'user': action == 'view',
        'guest': action == 'view',
    }.get(user_type, False)


def has_group_perm(user_type, action, obj, ctnr):
    """
    Permissions for groups
    Groups are assigned a subnet
    """
    if not obj.subnet in [ip_range.subnet for ip_range in ctnr.ranges.all()]:
        return False

    return {
        'cyder_admin': True, #?
        'ctnr_admin': action == 'view', #?
        'user': action == 'view', #?
        'guest': action == 'view',
    }.get(user_type, False)


def has_node_perm(user_type, action, obj, ctnr):
    """
    Permissions for nodes
    Nodes are assigned a ctnr
    """
    if obj.ctnr != ctnr:
        return False

    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == 'view',
    }.get(user_type, False)


def has_dhcp_option_perm(user_type, action, obj, ctnr):
    """
    Permissions for dhcp-related options
    DHCP options are global like SOAs, related to subnets and ranges
    """
    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == 'view',
    }.get(user_type, False)
