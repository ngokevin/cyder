from django.db import models
from cyder.cydns.reverse_domain.models import Reverse_Domain, ip_to_reverse_domain,ReverseDomainNotFoundError
import ipaddr
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
    IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    id              = models.AutoField(primary_key=True)
    ip_upper        = models.BigIntegerField(null=False)
    ip_lower        = models.BigIntegerField(null=False)
    reverse_domain  = models.ForeignKey(Reverse_Domain, null=False)
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES)

    def __str__(self):
        if self.ip_type == '4':
            return ipaddr.IPv4Address(self.ip_lower).__str__()
        if self.ip_type == '6':
            return ipaddr.IPv6Address((self.ip_upper*(2**64))+self.ip_lower).__str__()
    def __int__(self):
        if self.ip_type == '4':
            return ipaddr.IPv4Address(self.ip_lower).__int__()
        if self.ip_type == '6':
            return ipaddr.IPv6Address((self.ip_upper*(2**64))+self.ip_lower).__int__()

    def __repr__(self):
        return "<Ip '%s'>" % (self.__str__())


    class Meta:
        db_table = 'ip'

def add_str_ipv4(addr):
    if type(addr) is not type(''):
        raise ValueError
    try:
        ip = ipaddr.IPv4Address(addr)
    except ipaddr.AddressValueError, e:
        "Error in creating new ip."
        print str(e)
        return False
    try:
        ip_str = ip.__str__()
        reverse_domain = ip_to_reverse_domain( ip_str )
    except ReverseDomainNotFoundError:
        raise

    new_ip = Ip( ip_upper = 0, ip_lower = ip.__int__(), reverse_domain = reverse_domain, ip_type = '4')
    new_ip.save()
    return new_ip



def add_str_ipv6(addr):
    try:
        ip = ipaddr.IPv6Address(addr)
    except ipaddr.AddressValueError, e:
        print str(e)
        return False
    ip_upper, ip_lower = ipv6_to_longs( ip.__str__() )
    try:
        ip_str = ip.__str__()
        reverse_domain = ip_to_reverse_domain( ip_str, split=':' )
    except ReverseDomainNotFoundError:
        raise
    ip_upper, ip_lower = ipv6_to_longs(ip.__int__())
    new_ip = Ip( ip_upper = ip_upper, ip_lower = ip_lower, reverse_domain = reverse_domain, ip_type='6')
    new_ip.save()
    return new_ip


def ipv6_to_longs(addr):
    ip = ipaddr.IPv6Address(addr)
    ip_upper = ip._ip >> 64 # Put the last 64 bits in the first 64
    ip_lower = ip._ip & (1 << 64)-1 # Mask off the last sixty four bits
    return (ip_upper, ip_lower)
