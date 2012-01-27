from django.db import models
from cyder.cydns.reverse_domain.models import Reverse_Domain, ip_to_reverse_domain,ReverseDomainNotFoundError
from cyder.cydns.models import CyAddressValueError
import ipaddr
import pdb


class Ip( models.Model ):
    """Ip represents either an IPv4 or IPv6 address. All A, CNAME, PTR, and any other classes that use an ip will import and use this class.

    note::
        Django's BigInteger wasn't "Big" enough, so there is code in `cyder/cydns/ip/sql/ip.sql` that
        Alters the IP table.
    """
    IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    id              = models.AutoField(primary_key=True)
    ip_upper        = models.BigIntegerField(null=False)
    ip_lower        = models.BigIntegerField(null=False)
    reverse_domain  = models.ForeignKey(Reverse_Domain, null=False)
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=False)

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
    """This function will add an IPv4 address to the database.

    :param addr: IPv4 address to be added.
    :type addr: str
    :returns: new_ip -- Ip object
    :raises: ValueError, AddressValueError, ReverseDomainNotFoundError
    """
    if type(addr) is not type(''):
        raise CyAddressValueError("Invalid ip %s for IPv4s." % (addr) )
    ip = ipaddr.IPv4Address(addr) # TODO, this needs a try catch, which catches CyAddressValueError
    try:
        ip_str = ip.__str__() # TODO. Skip this and just use ip.__str__()
        reverse_domain = ip_to_reverse_domain( ip_str, ip_type='4' )
    except ReverseDomainNotFoundError:
        raise

    new_ip = Ip( ip_upper = 0, ip_lower = ip.__int__(), reverse_domain = reverse_domain, ip_type = '4')
    new_ip.save()
    return new_ip



def add_str_ipv6(addr):
    """This function will add an IPv6 address to the database.

    :param addr: IPv6 address to be added.
    :type addr: str
    :returns: new_ip -- Ip object
    :raises: AddressValueError, ReverseDomainNotFoundError
    """
    if type(addr) is not type(''):
        raise CyAddressValueError("Invalid ip %s for IPv6s." % (addr) )
    try:
        ip = ipaddr.IPv6Address(addr)
    except ipaddr.AddressValueError, e:
        raise CyAddressValueError("Invalid ip %s for IPv6s." % (addr) )

    ip_upper, ip_lower = ipv6_to_longs( ip.__str__() ) # Don't do this twice. (remove)
    try:
        ip_str = ip.__str__() # TODO skip this step.
        reverse_domain = ip_to_reverse_domain( ip_str, ip_type='6' )
    except ReverseDomainNotFoundError:
        raise
    ip_upper, ip_lower = ipv6_to_longs(ip.__int__())
    new_ip = Ip( ip_upper = ip_upper, ip_lower = ip_lower, reverse_domain = reverse_domain, ip_type='6')
    new_ip.save()
    return new_ip


def ipv6_to_longs(addr):
    """This function will turn an IPv6 into two long. The first will be reprsenting the first 64 bits of the address and second will be the lower 64 bits.

    :param addr: IPv6 to be converted.
    :type addr: str
    :returns: (ip_upper, ip_lower) -- (int, int)
    :raises: AddressValueError
    """
    try:
        ip = ipaddr.IPv6Address(addr)
    except ipaddr.AddressValueError, e:
        raise # TODO, this needs to be CyAddressValueError
    ip_upper = ip._ip >> 64 # Put the last 64 bits in the first 64
    ip_lower = ip._ip & (1 << 64)-1 # Mask off the last sixty four bits
    return (ip_upper, ip_lower)

