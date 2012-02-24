from django.db import models
from django import forms

from django.db import models
from cyder.cydns.reverse_domain.models import ReverseDomain, ip_to_reverse_domain,ReverseDomainNotFoundError
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
    ip_str          = models.CharField(max_length=39, editable=True)
    ip_upper        = models.BigIntegerField(null=False)
    ip_lower        = models.BigIntegerField(null=False)
    reverse_domain  = models.ForeignKey(ReverseDomain, null=False)
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=True)

    def __init__(self, *args, **kwargs):
        super(Ip, self).__init__(*args, **kwargs)

    def clean(self, update_reverse_domain=True):
        if self.ip_type not in ('4', '6'):
            raise CyAddressValueError("Error: Plase provide the type of IP")
        if type(self.ip_str) != type('') and type(self.ip_str) != type(u''):
            raise CyAddressValueError("Error: Plase provide the string representation of the IP")
        if self.ip_type == '4':
            try:
                ip = ipaddr.IPv4Address(self.ip_str)
                self.ip_str = ip.__str__()
            except ipaddr.AddressValueError, e:
                raise CyAddressValueError("Error: Invalid Ip address %s" % (self.ip_str))
            if update_reverse_domain:
                self.reverse_domain = ip_to_reverse_domain( self.ip_str, ip_type='4' )
            self.ip_upper = 0
            self.ip_lower = ip.__int__()
        else:
            try:
                ip = ipaddr.IPv6Address(self.ip_str)
                self.ip_str = ip.__str__()
            except ipaddr.AddressValueError, e:
                raise CyAddressValueError("Invalid ip %s for IPv6s." % (self.ip_str) )

            if update_reverse_domain:
                self.reverse_domain = ip_to_reverse_domain( self.ip_str, ip_type='6' )
            self.ip_upper, self.ip_lower =  ipv6_to_longs(ip.__int__())


    def delete(self, *args, **kwargs):
        super(Ip, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if kwargs.has_key('update_reverse_domain'):
            urd = kwargs.pop('update_reverse_domain')
        else:
            urd = True # Defualt

        self.clean( update_reverse_domain = urd )
        super(Ip, self).save(*args, **kwargs)

    def __str__(self):
        return self.ip_str
    def __int__(self):
        if self.ip_type == '4':
            self.ip_lower
        if self.ip_type == '6':
            return (self.ip_upper*(2**64))+self.ip_lower

    def __repr__(self):
        return "<Ip '%s'>" % (self.__str__())


    class Meta:
        db_table = 'ip'


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
        raise CyAddressValueError("Error: Invalid Ip address %s" % (addr))
    ip_upper = ip._ip >> 64 # Put the last 64 bits in the first 64
    ip_lower = ip._ip & (1 << 64)-1 # Mask off the last sixty four bits
    return (ip_upper, ip_lower)

