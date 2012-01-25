from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ip_to_reverse_domain, ReverseDomainNotFoundError
from cyder.cydns.ip.models import Ip
from cyder.cydns.models import CyAddressValueError

class PTR( models.Model ):
    """A PTR is used to map an IP to a domain name"""
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=256)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=True)

    def __str__(self):
        if self.name:
            fqdn = self.name+"."+self.domian.name
        else:
            fqdn = self.domain.name
        return "<PTR '%s %s %s'>" % (self.ip.__str__(), 'PTR', )
    def __repr__(self):
        return  self.__str__()

    class Meta:
        db_table = 'ptr'

class PTRNotFoundError(Exception):
    """This exception is thrown when you try to access a PTR that isn't in the database.
    """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

class PTRExistsError(Exception):
    """This exception is thrown when you try to create a PTR that already exists.
    """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

def _add_generic_ptr( ip, name, domain, ip_type ):
    """A generic add function for both the IPv4 and IPv6 add functions.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param name: The name the pointer should point to.
        :type  name: 'str'
        :param domain: The domain the pointer should point to.
        :type  domain: 'str'
        :param ip_type: Type of PTR ('4' or '6')
        :type  ip_type: 'str'
        notes::
            This function isn't complete TODO.
            See docs on how this function *should* work. There are going to have to be some shuffeling at the domain
            level for this to be fully implemented. For now, just set name=fqdn and domain=Null
    """

def add_ipv4_ptr( ip, fqdn ):
    """Add an PTR for an IPv4 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRExistsErrorError, ReverseDomainNotFoundError, CyAddressValueError, InvalidRecordNameError

    """
def add_ipv6_ptr( ip, fqdn ):
    """Add an PTR for an IPv6 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRExistsErrorError, ReverseDomainNotFoundError, CyAddressValueError, InvalidRecordNameError
    """
def remove_ipv4_ptr( ip, fqdn ):
    """Remove an PTR for an IPv4 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRNotFoundError
    """

def remove_ipv6_ptr( ip, fqdn ):
    """Remove an PTR for an IPv6 address.

        :param ip: Ip address of the PTR
        :type  ip: 'str'
        :param fqdn: The fqdn the pointer will point to.
        :type  fqdn: 'str'
        :raises: PTRNotFoundError
    """

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

