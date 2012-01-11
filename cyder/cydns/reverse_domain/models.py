from django.db import models
from cyder.cydns.soa.models import Soa
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

class ReverseDomainNotFoundError(Exception):
    """This exception is thrown when you are trying to add an Ip to the database and it cannot be paired with a reverse domain. The solution is to create a reverse domain for the Ip to live in.
    """
    def __str__(self):
        return "No reverse domain found. Condisder creating one."

class ReverseDomainExistsError(Exception):
    """This exception is thrown when you try to create a reverse domain that already exists."""
    def __str__(self):
        return "Reverse domain already exists."

class ReverseChildDomainExistsError(Exception):
    """This exception is thrown when you try to delete a reverse domain that has child reverese domains. A reverse domain should only be deleted when it has no child reverse domains."""
    def __str__(self):
        return "Child domains exist for this reverse domain."
class MasterReverseDomainNotFoundError(Exception):
    """All reverse domains should have a logical master (or parent) reverse domain. If you try to create a reverse domain that should have a master reverse domain and *doesn't* this exception is thrown."""
    def __str__(self):
        return "Master Reverse Domain not found. Please create it."

def ip_to_reverse_domain( ip, ip_type ):
    """Given an ip return the most specific reverse domain that the ip can belong to.

    :param name: ip
    :type name: str
    :param name: ip_type
    :type name: str -- '4' or '6'
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
        raise ReverseDomainNotFoundError

"""
Given an name return the most specific reverse_domain that the ip can belong to.
@param: name
@return: reverse_domain

A name x.y.z can be split up into x y and z. The reverse_domains, 'y.z' and 'z' should exist.
@return master_reverse_domain if valid reverse_domain
        None if invalid dname is a TLD.
        Throws an MasterReverseDomainNotFoundError if you passed it a dname that doens't have a
        master domain
"""
def _dname_to_master_reverse_domain( dname, ip_type="4" ):
    """Given an name return the most specific reverse_domain that the ip can belong to.

    note::

        A name x.y.z can be split up into x y and z. The reverse_domains, 'y.z' and 'z' should exist.

    :param name: dname
    :type name: str
    :param name: ip_type
    :type name: str -- '4' or '6'
    :returns: reverse_domain -- Reverse_Domain object
    :raises: MasterReverseDomainNotFoundError
    """
    dname = dname.rstrip('.')
    tokens = dname.split('.')
    master_reverse_domain = None
    for i in reversed(range(1,len(tokens))):
        parent_dname = '.'.join(tokens[:-i])
        possible_master_reverse_domain = Reverse_Domain.objects.filter( name = parent_dname, ip_type=ip_type )
        if not possible_master_reverse_domain:
            raise MasterReverseDomainNotFoundError
        else:
            master_reverse_domain = possible_master_reverse_domain[0]
    return master_reverse_domain

def boot_strap_add_ipv6_reverse_domain( ip ):
    """This function is here to help create IPv6 reverse domains.

    note::
        Every nibble in the reverse domain should not exists for this function to exit successfully.


    :param name: ip
    :type name: str
    :raises: ReverseDomainNotFoundError
    """
    for i in range(1,len(ip)+1,2):
        cur_reverse_domain = ip[:i]
        reverse_domain = add_reverse_domain( cur_reverse_domain, ip_type='6' )
    return reverse_domain

def add_reverse_domain( dname, ip_type ):
    """This function adds a reverse domain.

    :param name: dname
    :type name: str
    :param name: ip_type
    :type name: str
    :raises: ReverseDomainExistsError
    """
    if Reverse_Domain.objects.filter( name = dname ):
        raise ReverseDomainExistsError
    #For now just add it. MUST ADD LOGIC HERE TODO
    if ip_type == '6':
        dname = dname.lower()

    master_reverse_domain = _dname_to_master_reverse_domain( dname, ip_type=ip_type )
    if not master_reverse_domain:
        soa = None
    else:
        soa = master_reverse_domain.soa

    reverse_domain = Reverse_Domain( name=dname, master_reverse_domain=master_reverse_domain, soa=soa, ip_type=ip_type )
    reverse_domain.save()
    _reassign_reverse_ipv4_ips( reverse_domain, master_reverse_domain, ip_type )
    return reverse_domain

"""
reverse_domain_1 <-- get's 0 or more new ip's
"""
def _reassign_reverse_ipv4_ips( reverse_domain_1, reverse_domain_2, ip_type ):
    """There are some formalities that need to happen when a reverse domain is added and deleted. For example, when adding say we had the ip address 128.193.4.0 and it had the reverse_domain 128.193. If we add the reverse_domain 128.193.4, our 128.193.4.0 no longer belongs to the 128.193 domain. We need to re-asign the ip to it's correct reverse domain.

    :param name: reverse_domain_1
    :type name: str
    :param name: reverse_domain_2
    :type name: str
    """

    if reverse_domain_2 is None:
        return
    ips = reverse_domain_2.ip_set.iterator()
    for ip in ips:
        correct_reverse_domain = ip_to_reverse_domain( ip.__str__(), ip_type=ip_type )
        if correct_reverse_domain != ip.reverse_domain:
            ip.reverse_domain = correct_reverse_domain
            ip.save()

def remove_reverse_domain( dname, ip_type ):
    """This function removes a reverse domain.

    :param name: dname
    :type name: str
    :param name: ip_type
    :type name: str
    :raises: ReverseDomainExistsError

    notes::
        Think about reverse_domains (and domains for that matter) as a tree. This function is only
        defined to work on _leaf nodes_. If you attempt to remove a none leaf reverse_domain a
        ReverseChildDomainExistsError will be thrown.
    """
    if not Reverse_Domain.objects.filter( name = dname, ip_type = ip_type ):
        raise ReverseDomainNotFoundError
    reverse_domain = Reverse_Domain.objects.filter( name = dname, ip_type = ip_type )[0] # It's cached
    ips = reverse_domain.ip_set.iterator()
    for ip in ips:
        ip.reverse_domain = reverse_domain.master_reverse_domain
        ip.save()
    reverse_domain.delete()


"""
Use ipaddr.IPv6Address('2001:0db8:85a3:0002:0:0:0:2').__str__()
this will represent the ip in a consisten manner.
"""
def add_reverse_ipv6_domain( name ):
    #For now just add it. MUST ADD LOGIC HERE TODO
    try:
        ip = ipaddr.IPv6Address(name)
    except ipaddr.AddressValueError, e:
        raise

    possible_master_reverse_domain = '.'.join(ip_name.split('.')[:-1]) # Remove the last block
    # 1238:1234:1234 -> becomes -> 1238:1234 (which is the master domain)

    # Check for a domain that already exists.
    if Reverse_Domain.objects.filter( name=ip_name ):
        raise ReverseDomainExistsError

    master_reverse_domain = None
    if not possible_master_reverse_domain:
        soa = None
    else:
        # Inherit SOA from master
        master_reverse_domain = Reverse_Domain.objects.filter( name = possible_master_reverse_domain )[0]
        soa = master_reverse_domain.soa


    reverse_domain = Reverse_Domain( name=ip_name, master_reverse_domain=None, soa=soa )
    reverse_domain.save()
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
    ip_str = ipaddr.IPv6Address(addr).exploded
    return '.'.join(list(ip_str.replace(':','')))
