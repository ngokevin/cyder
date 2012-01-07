from django.db import models
from cyder.cydns.soa.models import Soa
import ipaddr
import pdb

class Reverse_Domain( models.Model ):
    id                      = models.AutoField(primary_key=True)
    name                    = models.CharField(max_length=100)
    master_reverse_domain   = models.ForeignKey("self", null=True)
    soa                     = models.ForeignKey(Soa, null=True)

    class Meta:
        db_table = 'reverse_domain'

class ReverseDomainNotFoundError(Exception):
    def __str__(self):
        return "No reverse domain found. Condisder creating one."

class ReverseDomainExistsError(Exception):
    def __str__(self):
        return "Reverse domain already exists."

class ReverseChildDomainExistsError(Exception):
    def __str__(self):
        return "Child domains exist for this reverse domain."
class MasterReverseDomainNotFoundError(Exception):
    def __str__(self):
        return "Master Reverse Domain not found. Please create it."

"""
Given an ip return the most specific reverse domain that the ip can belong to.
@param: ip <ipaddr.IpAddres>
@return: Reverse_Domain <'object'>
"""
def ip_to_reverse_domain( ip, split='.' ):
    octets = ip.split(split)
    for i in reversed(range(len(octets)+1)):
        search_reverse_domain = split.join(octets[:i])
        rev_dom = Reverse_Domain.objects.filter( name = search_reverse_domain )
        if rev_dom:
            return rev_dom
        else:
            continue
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
def _dname_to_master_reverse_domain( dname, split='.' ):
    tokens = dname.split(split)
    master_reverse_domain = None
    for i in reversed(range(len(tokens)-1)):
        parent_dname = split.join(tokens[i+1:])
        master_reveres_domain = Reverse_Domain.objects.filter( name = parent_dname )
        if not master_reverse_domain:
            raise MasterReverseDomainNotFoundError
    return master_reverse_domain

"""
This function is here to help create IPv6 reverse domains.
@dname: ipv6 network. i.e. 2001:0db8:85a3:0000
                    block   1    2    3    4

The funciton should attempt to create block 1, block 2 ... block n.
@return True if succesfull
@exceptions ReverseDomainExistsError if it finds that any of the blocks already exist.
"""
def boot_strap_add_ipv6_reverse_domain( dname ):
    ip = ipaddr.IPv6Address(dname).__str__().rstrip(':').split(':')
    for i in range(len(ip)):
        tmp = ':'.join(ip[:i+1])
        cur_reverse_domain = tmp.rstrip(':')
        if i < 7:
            cur_reverse_domain += "::"
        add_reverse_ipv6_domain( cur_reverse_domain )
    return True

"""
There are some formalities that need to happen when a reverse domain is added and deleted.
For example, when adding say we had the ip address 128.193.4.0 and it had the
reverse_domain 128.193. If we add the reverse_domain 128.193.4, our 128.193.4.0 no longer
belongs to the 128.193 domain. We need to re-asign the ip to it's correct reverse domain.
Given a new_domain the add function needs to:
    1) Get all new_domain's master_domain.
    2) Get all ip's that belong to the master_domain.
        * if any ip's now belong to the new reverse_domain, reassign the ip to the new_domain
"""
def add_reverse_ipv4_domain( name ):
    #For now just add it. MUST ADD LOGIC HERE TODO

    if master_reverse_domain is None:
        soa = None
    else:
        soa = master_reverse_domain.soa

    _dname_to_master_reverse_domain( dname ) # This function runs sanity checks
    if Domain.objects.filter( name = dname ):
        raise DomainExistsError


    reverse_domain = Reverse_Domain( name=name, master_reverse_domain=None, soa=soa )
    reverse_domain.save()
    return reverse_domain
"""
Given a del_domain the remove function needs to:
    1) Make sure del_domain exists. Through ReverseDomainNotFoundError if it doesn't.
    2) Get all del_domain's master_domain.
    3) Get all ip's that belong to the del_domain.
        * reassign all del_domain ip's to it's master domain.
    Note: Think about reverse_domains (and domains for that matter) as a tree. This function is only
        defined to work on _leaf nodes_. If you attempt to remove a none leaf reverse_domain a
        ReverseChildDomainExistsError will be thrown.
"""
def remove_reverse_ipv4_domain( name ):
    pass


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

    ip_name = ip.__str__().rstrip(':') #Get rid of trailing ':'
    possible_master_domain = ':'.join(ip_name.split(':')[:-1]) # Remove the last block
    # 1238:1234:1234 -> becomes -> 1238:1234 (which is the master domain)

    master_reverse_domain = None
    if not possible_master_domain:
        soa = None
    else:
        # Inherit SOA from master
        master_reverse_domain = Reverse_Domain.objects.filter( name = possible_master_domain )[0]
        soa = master_reverse_domain.soa

    # Check for a domain that already exists.
    if Reverse_Domain.objects.filter( name=ip_name ):
        raise ReverseDomainExistsError

    reverse_domain = Reverse_Domain( name=ip_name, master_reverse_domain=None, soa=soa )
    reverse_domain.save()
