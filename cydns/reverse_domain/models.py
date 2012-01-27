from django.db import models
from cyder.cydns.soa.models import Soa
from cyder.cydns.models import _validate_name, _validate_reverse_name, CyAddressValueError
from cyder.cydns.cydns import trace
import ipaddr
import pdb

class Reverse_Domain( models.Model ):
    """A reverse DNS domain is used build reverse bind files."""
    IP_TYPE_CHOICES = ( ('4','IPv4'),('6','IPv6') )
    id                      = models.AutoField(primary_key=True)
    name                    = models.CharField(max_length=100)
    master_reverse_domain   = models.ForeignKey("self", null=True)
    soa                     = models.ForeignKey(Soa, null=True)
    ip_type                 = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, default='4')

    def __str__(self):
        return "<Reverse_Domain '%s'>" % (self.name)
    def __repr__(self):
        return  self.__str__()

    class Meta:
        db_table = 'reverse_domain'

#TODO. Subclass These exceptions.
class ReverseDomainNotFoundError(Exception):
    """This exception is thrown when you are trying to add an Ip to the database and it cannot be paired with a reverse domain. The solution is to create a reverse domain for the Ip to live in.
    """
    def __init__(self, msg ):
        self.msg = msg
    def __str__(self):
        return self.msg
    def __repr__(self):
        return  self.__str__()

class ReverseDomainExistsError(Exception):
    """This exception is thrown when you try to create a reverse domain that already exists."""
    def __init__(self, msg ):
        self.msg = msg
    def __str__(self):
        return self.msg
    def __repr__(self):
        return  self.__str__()
class ReverseChildDomainExistsError(Exception):
    """This exception is thrown when you try to delete a reverse domain that has child reverese domains. A reverse domain should only be deleted when it has no child reverse domains."""
    def __init__(self, msg ):
        self.msg = msg
    def __str__(self):
        return self.msg
    def __repr__(self):
        return  self.__str__()

class MasterReverseDomainNotFoundError(Exception):
    """All reverse domains should have a logical master (or parent) reverse domain. If you try to create a reverse domain that should have a master reverse domain and *doesn't* this exception is thrown."""
    def __init__(self, msg ):
        self.msg = msg
    def __str__(self):
        return self.msg
    def __repr__(self):
        return  self.__str__()

def ip_to_reverse_domain( ip, ip_type ):
    """Given an ip return the most specific reverse domain that the ip can belong to.

    :param ip: The ip to which we are using to search for a reverse domain.
    :type ip: str
    :param ip_type: The type of Ip address ip is. It should be either an IPv4 or IPv6 address.
    :type ip_type: str -- '4' or '6'
    :returns: reverse_domain -- Reverse_Domain object
    :raises: ReverseDomainNotFoundError
    """
    if ip_type == '6':
        ip = nibblize(ip)
    tokens = ip.split('.')
    reverse_domain = None
    for i in reversed(range(1,len(tokens))):
        search_reverse_domain = '.'.join(tokens[:-i])
        tmp_reverse_domain = Reverse_Domain.objects.filter( name = search_reverse_domain, ip_type=ip_type )
        if tmp_reverse_domain:
            reverse_domain = tmp_reverse_domain[0]
        else:
            break # Since we have a full tree we must have reached a leaf node.
    if reverse_domain:
        return reverse_domain
    else:
        raise ReverseDomainNotFoundError("Error: Could not find reverse domain for ip '%s'" % (ip))

def _dname_to_master_reverse_domain( dname, ip_type="4" ):
    """Given an name return the most specific reverse_domain that the ip can belong to.

    note::
        A name x.y.z can be split up into x y and z. The reverse_domains, 'y.z' and 'z' should exist.

    :param dname: The domain which we are using to search for a master reverse domain.
    :type dname: str
    :param ip_type: The type of reverse domain. It should be either an IPv4 or IPv6 address.
    :type ip_type: str -- '4' or '6'
    :returns: Reverse_Domain or None -- None if the reverse domain is a TLD
    :raises: MasterReverseDomainNotFoundError
    """
    tokens = dname.split('.')
    master_reverse_domain = None
    for i in reversed(range(1,len(tokens))):
        parent_dname = '.'.join(tokens[:-i])
        possible_master_reverse_domain = Reverse_Domain.objects.filter( name = parent_dname, ip_type=ip_type )
        if not possible_master_reverse_domain:
            raise MasterReverseDomainNotFoundError("Error: Coud not find master domain for %s.\
                                                                Consider creating it." % (dname))
        else:
            master_reverse_domain = possible_master_reverse_domain[0]
    return master_reverse_domain


def _add_generic_reverse_domain( dname, ip_type ):
    _validate_reverse_name( dname, ip_type )
    if Reverse_Domain.objects.filter( name = dname ):
        raise ReverseDomainExistsError( "Error: The reverse domain %s already exists." % (dname) )

    if ip_type == '6':
        dname = dname.lower()

    master_reverse_domain = _dname_to_master_reverse_domain( dname, ip_type=ip_type )
    if not master_reverse_domain:
        soa = None
    else:
        soa = master_reverse_domain.soa

    reverse_domain = Reverse_Domain( name=dname, master_reverse_domain=master_reverse_domain, soa=soa, ip_type=ip_type )
    reverse_domain.save()
    _reassign_reverse_ips( reverse_domain, master_reverse_domain, ip_type )
    return reverse_domain

def _remove_generic_reverse_domain( dname, ip_type ):
    _validate_reverse_name( dname, ip_type )
    if not Reverse_Domain.objects.filter( name = dname, ip_type = ip_type ):
        raise ReverseDomainNotFoundError( "Error: %s was not found." % (dname))
    reverse_domain = Reverse_Domain.objects.filter( name = dname, ip_type = ip_type )[0] # It's cached

    # Check if it has children.
    children = Reverse_Domain.objects.filter( master_reverse_domain = reverse_domain )
    if children:
        error = ""
        for child in children:
            error += child.__str__()+", "
        raise ReverseChildDomainExistsError("Error: Domain %s has children: %s" % (dname, error))

    ips = reverse_domain.ip_set.iterator()
    for ip in ips:
        ip.reverse_domain = reverse_domain.master_reverse_domain
        ip.save()
    reverse_domain.delete()

def _reassign_reverse_ips( reverse_domain_1, reverse_domain_2, ip_type ):
    """There are some formalities that need to happen when a reverse domain is added and deleted. For example, when adding say we had the ip address 128.193.4.0 and it had the reverse_domain 128.193. If we add the reverse_domain 128.193.4, our 128.193.4.0 no longer belongs to the 128.193 domain. We need to re-asign the ip to it's correct reverse domain.

    :param reverse_domain_1: The domain which could possible have addresses added to it.
    :type reverse_domain_1: str
    :param reverse_domain_2: The domain that has ip's which might not belong to it anymore.
    :type reverse_domain_2: str
    """

    if reverse_domain_2 is None:
        return
    ips = reverse_domain_2.ip_set.iterator()
    for ip in ips:
        correct_reverse_domain = ip_to_reverse_domain( ip.__str__(), ip_type=ip_type )
        if correct_reverse_domain != ip.reverse_domain:
            ip.reverse_domain = correct_reverse_domain
            ip.save()

def boot_strap_add_ipv6_reverse_domain( ip ):
    """This function is here to help create IPv6 reverse domains.

    .. note::
        Every nibble in the reverse domain should not exists for this function to exit successfully.


    :param ip: The ip address in nibble format
    :type ip: str
    :raises: ReverseDomainNotFoundError
    """
    _validate_reverse_name( ip, '6' )

    for i in range(1,len(ip)+1,2):
        cur_reverse_domain = ip[:i]
        reverse_domain = add_reverse_ipv6_domain( cur_reverse_domain )
    return reverse_domain


"""
@param: addr - A valid IPv6 string
@return: correct reverse zone representation
>>> nibblize('2620:0105:F000::1')
'2.6.2.0.0.1.0.5.F.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1'
>>> nibblize('2620:0105:F000:9::1')
'2.6.2.0.0.1.0.5.f.0.0.0.0.0.0.9.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1'
>>> nibblize('2620:0105:F000:9:0:1::1')
'2.6.2.0.0.1.0.5.f.0.0.0.0.0.0.9.0.0.0.0.0.0.0.1.0.0.0.0.0.0.0.1'
"""
def nibblize( addr ):
    """Given an IPv6 address is 'colon' format, return the address in 'nibble' form::

        nibblize('2620:0105:F000::1')
        '2.6.2.0.0.1.0.5.F.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1'

    :param addr: The ip address to convert
    :type addr: str
    """
    try:
        ip_str = ipaddr.IPv6Address(addr).exploded
    except ipaddr.AddressValueError, e:
        raise CyAddressValueError("Error: Invalid IPv6 address %s." % (addr))

    return '.'.join(list(ip_str.replace(':','')))

def add_reverse_ipv4_domain( dname ):
    """This function adds a an IPv4 reverse domain.

    :param dname: The reverse domain to be added.
    :type dname: str
    :param ip_type: The type of reverse domain. It should be either an IPv4 or IPv6 address.
    :type ip_type: str -- '4' or '6'
    :raises: ReverseDomainExistsError
    """
    return _add_generic_reverse_domain( dname, '4' )
def remove_reverse_ipv4_domain( dname ):
    """This function removes an IPv4 reverse domain.

    :param dname: The reverse domain to be removed.
    :type dname: str
    :param ip_type: The type of reverse domain. It should be either an IPv4 or IPv6 address.
    :type ip_type: str -- '4' or '6'
    :raises: ReverseDomainExistsError

    .. note::
        Think about reverse_domains (and domains for that matter) as a tree. This function is only
        defined to work on *leaf nodes*. If you attempt to remove a none leaf reverse_domain a
        ReverseChildDomainExistsError will be thrown.
    """
    return _remove_generic_reverse_domain( dname, '4' )
def add_reverse_ipv6_domain( dname ):
    """This function adds a an IPv6 reverse domain.

    :param dname: The reverse domain to be added.
    :type dname: str
    :param ip_type: The type of reverse domain. It should be either an IPv4 or IPv6 address.
    :type ip_type: str -- '4' or '6'
    :raises: ReverseDomainExistsError
    """
    return _add_generic_reverse_domain( dname, '6' )
def remove_reverse_ipv6_domain( dname ):
    """This function removes an IPv6 reverse domain.

    :param dname: The reverse domain to be removed.
    :type dname: str
    :param ip_type: The type of reverse domain. It should be either an IPv4 or IPv6 address.
    :type ip_type: str -- '4' or '6'
    :raises: ReverseDomainExistsError

    .. note::
        Think about reverse_domains (and domains for that matter) as a tree. This function is only
        defined to work on *leaf nodes*. If you attempt to remove a none leaf reverse_domain a
        ReverseChildDomainExistsError will be thrown.
    """
    return _remove_generic_reverse_domain( dname, '6' )
