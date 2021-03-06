from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.reverse_domain.models import ip_to_reverse_domain
from cyder.cydns.validation import validate_ip_type

import ipaddr

import pdb


class Ip(models.Model):
    """An ``Ip`` instance represents either an IPv4 or IPv6 address.

    ``Ip`` instances are used in ``AddressRecords`` (A and AAAA records)
    and in ``PTR`` records.

    ``Ip`` instances in a PTR record must be mapped back to a
    ``ReverseDomain`` object. A ``ValidationError`` is raised if an
    eligible ``ReverseDomain`` cannot be found when trying to create the
    ``PTR``'s ``Ip``.

    The reason why an IP must be mapped back to a ``ReverseDomain`` has
    to do with how bind files are written. In a reverse zone file, ip
    addresses are mapped from IP to DATA. For instance an PTR record
    would look like this::

        IP                  DATA
        197.1.1.1   PTR     foo.bob.com

    If we were building the file ``197.in-addr.arpa``, all IP addresses
    in the ``197`` domain would need to be in this file. To reduce the
    complexity of finding records for a reverse domain, an ``IP`` is
    linked to it's appropriate reverse domain when it is created. It's
    mapping is updated when it's reverse domain is deleted or a more
    appropritate reverse domain is added.  Keeping the ``Ip`` feild on
    PTR  will help preformance when building reverse zone files.

    The algorithm for determineing which reverse domain an ``Ip``
    belongs to is done by applying a `longest prefix match` to all
    reverse domains in the ``ReverseDomain`` table.

    ``AddressRecords`` need the validation that happens in this class
    but do not need their ``Ip``'s to be tied back to a reverse domain.

    .. note::
        Django's BigInteger wasn't "Big" enough, so there is code
        in `cyder/cydns/ip/sql/ip.sql` that Alters the IP table.

    """
    IP_TYPE_CHOICES = (('4', 'ipv4'), ('6', 'ipv6'))
    ip_str = models.CharField(max_length=39, editable=True)
    # ip_upper/lower are calculated from ip_str on ip_clean.
    ip_upper = models.BigIntegerField(null=False, blank=True)
    ip_lower = models.BigIntegerField(null=False, blank=True)
    # TODO, should reverse_domain go into the PTR model?  I would think
    # it shouldn't because it is used in this class during the ip_clean
    # function.  Technically the ip_clean function would work if the
    # field existed in the PTR model, but overall it would hurt
    # readability.
    #
    # reactor.addCallback(think_about_it)
    reverse_domain = models.ForeignKey(ReverseDomain, null=True, blank=True)
    ip_type = models.CharField(max_length=1, choices=IP_TYPE_CHOICES,
                               editable=True)

    class Meta:
        abstract = True

    def clean_ip(self, update_reverse_domain=True):
        """The clean method in Ip is different from the rest. It needs
        to be called with the update_reverse_domain flag. Sometimes we
        need to not update the reverse domain of an IP (i.e. when we are
        deleting a reverse_domain).
        """
        # TODO, it's a fucking hack. Car babies.
        validate_ip_type(self.ip_type)
        self._validate_ip_str()
        if self.ip_type == '4':
            try:
                ip = ipaddr.IPv4Address(self.ip_str)
                self.ip_str = str(ip)
            except ipaddr.AddressValueError, e:
                raise ValidationError("Invalid Ip address {0}".
                                      format(self.ip_str))
            if update_reverse_domain:
                self.reverse_domain = ip_to_reverse_domain(self.ip_str,
                                                           ip_type='4')
            self.ip_upper = 0
            self.ip_lower = int(ip)
        else:
            try:
                ip = ipaddr.IPv6Address(self.ip_str)
                self.ip_str = str(ip)
            except ipaddr.AddressValueError, e:
                raise ValidationError("Invalid ip {0} for IPv6s.".
                                      format(self.ip_str))

            if update_reverse_domain:
                self.reverse_domain = ip_to_reverse_domain(self.ip_str,
                                                           ip_type='6')
            self.ip_upper, self.ip_lower = ipv6_to_longs(int(ip))

    def __int__(self):
        if self.ip_type == '4':
            self.ip_lower
        if self.ip_type == '6':
            return (self.ip_upper * (2 ** 64)) + self.ip_lower

    def _validate_ip_str(self):
        if isinstance(self.ip_str, str) or isinstance(self.ip_str, unicode):
            return
        else:
            raise ValidationError("Plase provide the string representation"
                                  "of the IP")


def ipv6_to_longs(addr):
    """This function will turn an IPv6 into two longs. The first number
    represents the first 64 bits of the address and second represents
    the lower 64 bits.

    :param addr: IPv6 to be converted.
    :type addr: str
    :returns: (ip_upper, ip_lower) -- (int, int)
    :raises: ValidationError
    """
    try:
        ip = ipaddr.IPv6Address(addr)
    except ipaddr.AddressValueError, e:
        raise ValidationError("AddressValueError: Invalid Ip address {0}".
                              format(addr))
    ip_upper = ip._ip >> 64  # Put the last 64 bits in the first 64
    ip_lower = ip._ip & (1 << 64) - 1  # Mask off the last sixty four bits
    return (ip_upper, ip_lower)
