from django.db import models
from cyder.cydns.reverse_domain.models import Reverse_Domain, ip_to_reverse_domain,ReverseDomainNotFoundError
import ipaddr
from ipaddr import IPv4Address, IPv6Address
import pdb

"""
2001:0db8:85a3:0000:0000:8a2e:0370:7334
|-----------------| |------------------|
    *ip_upper*              128.193.0.0
                            *ip_lower*

TODO
Data Validation
---------------
* If ipv4, ip_upper == 0
* If ipv4, ip_lower < 4294967295

"""

class Ip( models.Model ):
    id              = models.AutoField(primary_key=True)
    ip_upper        = models.BigIntegerField(null=False)
    ip_lower        = models.BigIntegerField(null=False)
    reverse_domain  = models.ForeignKey(Reverse_Domain, null=False)


    class Meta:
        db_table = 'ip'

def add_str_ipv4(addr):
    if type(addr) is not type(''):
        raise ValueError
    try:
        ip = IPv4Address(addr)
    except ipaddr.AddressValueError, e:
        print str(e)
        return False
    try:
        ip_str = ip.__str__()
        reverse_domain = ip_to_reverse_domain( ip_str )[0]
    except ReverseDomainNotFoundError:
        raise

    new_ip = Ip( ip_upper = 0, ip_lower = ip.__int__(), reverse_domain = reverse_domain)
    new_ip.save()
    return new_ip



def add_str_ipv6(addr):
    try:
        ip = IPv6Address(addr)
    except ipaddr.AddressValueError, e:
        print str(e)
        return False
    ip_upper, ip_lower = ipv6_to_longs( ip.__str__() )
    try:
        ip_str = ip.__str__()
        reverse_domain = ip_to_reverse_domain( ip_str, split=':' )[0]
    except ReverseDomainNotFoundError:
        raise
    ip_upper, ip_lower = ipv6_to_longs(ip.__int__())
    new_ip = Ip( ip_upper = ip_upper, ip_lower = ip_lower, reverse_domain = reverse_domain)
    new_ip.save()
    return new_ip


def ipv6_to_longs(addr):
    ip = IPv6Address(addr)
    ip_upper = ip._ip >> 64 # Put the last 64 bits in the first 64
    ip_lower = ip._ip & (1 << 65)-1 # Mask off the last sixty four bits
    return (ip_upper, ip_lower)
