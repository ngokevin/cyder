from django.db import models
from django.core.exceptions import ValidationError
from django import forms

from cyder.cydns.reverse_domain.models import ReverseDomain, ip_to_reverse_domain

import ipaddr

import pdb


class Ip( models.Model ):
    """
    An ``Ip`` instance represents either an IPv4 or IPv6 address.

    ``Ip`` instances are used in ``AddressRecords`` (A and AAAA records) and in ``PTR`` records.
    All ``Ip`` instances must be mapped back to a ``ReverseDomain`` object. A ``ValidationError`` is
    raised if an eligible ``ReverseDomain`` cannot be found when trying to create an ``Ip``.

    The reason why an IP must be mapped back to a ``ReverseDomain`` has to do with how bind files
    are written. In a reverse zone file, ip addresses are mapped from IP to DATA. For instance an
    PTR record would look like this::

        IP                  DATA
        197.1.1.1   PTR     foo.bob.com

    If we were building the file ``197.in-addr.arpa``, all IP addresses in the ``197`` domain would
    need to be in this file. To reduce the complexity of finding records for a reverse domain an IP
    is linked to the appropriate reverse domain when it is created. It's mapping is updated when
    it's reverse domain is deleted or a more appropritate reverse domain is added. Note that keeping
    the ``Ip`` feild on PTR and ``AddressRecords`` will help preformance since both need to be
    searched.

    The algorithm for determineing which reverse domain an ``Ip`` belongs to is done by applying a
    `longest prefix match` to all reverse domains in the ``ReverseDomain`` table.

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

    class Meta:
        db_table = 'ip'

    def clean(self, update_reverse_domain=True):
        """ The clean method in Ip is different from the rest. It needs to be called with the
            update_reverse_domain flag. Sometimes we need to not update the reverse domain of
            an IP (i.e. when we are deleting a reverse_domain).

            Basically, we need fine grain control over the save and clean function so we are
            not using full_clean.
        """
        # TODO, it's a fucking hack. Car babies.
        self._validate_ip_type()
        self._validate_ip_str()
        if self.ip_type == '4':
            try:
                ip = ipaddr.IPv4Address(self.ip_str)
                self.ip_str = str(ip)
            except ipaddr.AddressValueError, e:
                raise ValidationError("AddressValueError: Invalid Ip address %s" % (self.ip_str))
            if update_reverse_domain:
                self.reverse_domain = ip_to_reverse_domain( self.ip_str, ip_type='4' )
            self.ip_upper = 0
            self.ip_lower = int(ip)
        else:
            try:
                ip = ipaddr.IPv6Address(self.ip_str)
                self.ip_str = str(ip)
            except ipaddr.AddressValueError, e:
                raise ValidationError("AddressValueError: Invalid ip %s for IPv6s." % (self.ip_str) )

            if update_reverse_domain:
                self.reverse_domain = ip_to_reverse_domain( self.ip_str, ip_type='6' )
            self.ip_upper, self.ip_lower =  ipv6_to_longs(int(ip))

    def save(self, *args, **kwargs):
        if kwargs.has_key('update_reverse_domain'):
            urd = kwargs.pop('update_reverse_domain')
            self.clean( update_reverse_domain = urd )
        else:
            self.clean()
        super(Ip, self).save(*args, **kwargs)

    def __str__(self):
        return self.ip_str

    def __int__(self):
        if self.ip_type == '4':
            self.ip_lower
        if self.ip_type == '6':
            return (self.ip_upper*(2**64))+self.ip_lower

    def __repr__(self):
        return "<Ip '%s'>" % (str(self))

    def _validate_ip_type( self ):
        if self.ip_type not in ('4', '6'):
            raise ValidationError("Error: Plase provide the type of IP")

    def _validate_ip_str( self ):
        if type(self.ip_str) not in (str, unicode):
            raise ValidationError("Error: Plase provide the string representation of the IP")

def ipv6_to_longs(addr):
    """
    This function will turn an IPv6 into two longs. The first number represents the first 64 bits
    of the address and second represents the lower 64 bits.

    :param addr: IPv6 to be converted.
    :type addr: str
    :returns: (ip_upper, ip_lower) -- (int, int)
    :raises: ValidationError
    """
    try:
        ip = ipaddr.IPv6Address(addr)
    except ipaddr.AddressValueError, e:
        raise ValidationError("AddressValueError: Invalid Ip address %s" % (addr))
    ip_upper = ip._ip >> 64 # Put the last 64 bits in the first 64
    ip_lower = ip._ip & (1 << 64)-1 # Mask off the last sixty four bits
    return (ip_upper, ip_lower)

