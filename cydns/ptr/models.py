from django.db import models
from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.reverse_domain.models import ip_to_reverse_domain, ReverseDomainNotFoundError
from cyder.cydns.ip.models import Ip, ipv6_to_longs
from cyder.cydns.models import CyAddressValueError, _validate_name, RecordExistsError, RecordNotFoundError
from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6
from cyder.cydns.cydns import trace
import ipaddr

class PTR( models.Model ):
    """A PTR is used to map an IP to a domain name"""
    #IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    #ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=False)
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=256)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=True)

    def __str__(self):
        return "<Pointer '%s %s %s'>" % (self.ip.__str__(), 'PTR', self.name )
    def __repr__(self):
        return  self.__str__()

    class Meta:
        db_table = 'ptr'


def _add_generic_ptr( ip, name, ip_type ):
    """A generic add function for both the IPv4 and IPv6 add functions.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param name: The name the pointer should point to.
        :type  name: 'str'
        :param ip_type: Type of PTR ('4' or '6')
        :type  ip_type: 'str'
        notes::
    """
    _validate_name( name )
    # Leaving myself a comment. This exception handling is done int add_st_ipv*. It's not needed.
    try:
        if ip_type == '4':
            ip = add_str_ipv4( ip )
        else:
            ip = add_str_ipv6( ip )
    except ipaddr.AddressValueError, e:
        raise CyAddressValueError("Invalid ip %s for IPv%s." % (ip, ip_type) )

    exist = _check_exists( name, ip )
    if exist:
        raise RecordExistsError( "%s already exists." % (exist.__str__()) )

    domain = _name_to_domain( name )

    ptr = PTR( name = name, domain = domain, ip = ip )
    ptr.save()
    return ptr


def add_ipv4_ptr( ip, fqdn ):
    """Add an PTR for an IPv4 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRExistsErrorError, ReverseDomainNotFoundError, CyAddressValueError, InvalidRecordNameError

    """
    return _add_generic_ptr( ip, fqdn, '4' )



def add_ipv6_ptr( ip, fqdn ):
    """Add an PTR for an IPv6 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRExistsErrorError, ReverseDomainNotFoundError, CyAddressValueError, InvalidRecordNameError
    """
    return _add_generic_ptr( ip, fqdn, '6' )

def _remove_generic_ptr( ip, fqdn, ip_type ):
    if not (ip and fqdn and ip_type):
        raise RecordNotFoundError("Error: ip and fqdn are required for remove.")
    _validate_name( fqdn )
    try:
        if ip_type == '4':
            ip_upper, ip_lower = 0, ipaddr.IPv4Address(ip).__int__()
        else:
            ip_upper, ip_lower = ipv6_to_longs(ip)

    except ipaddr.AddressValueError, e:
        raise RecordNotFoundError("Error: The record %s %s %s was not found." % (fqdn,\
                                                'A' if ip_type == '4' else 'AAAA', ip) )
    ptr = _check_exists( fqdn, ip )
    if not ptr:
        raise RecordNotFoundError("Error: The record %s %s %s was not found." % (fqdn,\
                                                'A' if ip_type == '4' else 'AAAA', ip) )
    else:
        ptr.ip.delete()
        ptr.delete()


def remove_ipv4_ptr( ip, fqdn ):
    """Remove an PTR for an IPv4 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRNotFoundError
    """
    _remove_generic_ptr( str(ip), fqdn, '4' )

def remove_ipv6_ptr( ip, fqdn ):
    """Remove an PTR for an IPv6 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRNotFoundError
    """
    _remove_generic_ptr( str(ip), fqdn, '6' )

def _update_generic_ptr( ptr, new_fqdn, ip_type ):
    _validate_name( new_fqdn )
    exist = _check_exists( new_fqdn, ptr.ip )
    if exist:
        raise RecordExistsError( "%s already exists." % (exist.__str__()) )
    else:
        domain = _name_to_domain( new_fqdn )
        ptr.domain = domain
        ptr.name = new_fqdn
        ptr.save()
        return ptr


def update_ipv4_ptr( ptr, new_fqdn ):
    """Update an IPv4 PTR

        :param ptr: The ptr instance that is being updated.
        :type  ptr: Ptr
        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer currently points to.
        :type  fqdn: 'str'
        :param new_fqdn: The fqdn the pointer will point to after this function is called.
        :type  new_fqdn: 'str'
        :raises: PTRExistsErrorError, ReverseDomainNotFoundError, PTRNotFoundError, CyAddressValueError
    """
    return _update_generic_ptr( ptr, new_fqdn, '4' )

def update_ipv6_ptr( ptr, new_fqdn ):
    """Update an IPv6 PTR

        :param ptr: The ptr instance that is being updated.
        :type  ptr: Ptr
        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRExistsErrorError, ReverseDomainNotFoundError, PTRNotFoundError, CyAddressValueError
    """
    return _update_generic_ptr( ptr, new_fqdn, '6' )

def _check_exists( name, ip ):
    exist = PTR.objects.filter( name = name ).select_related('ip')
    for possible in exist:
        if possible.ip.__str__().lower() == ip.__str__().lower():
            return possible
