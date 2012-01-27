from django.db import models
from cyder.cydns.models import _validate_label, InvalidRecordNameError, CyAddressValueError
from cyder.cydns.models import _validate_name, RecordExistsError, RecordNotFoundError
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip, add_str_ipv4, add_str_ipv6, ipv6_to_longs
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain
import ipaddr
import string
import pdb

# This is the A and AAAA record class
class Address_Record( models.Model ):
    """Address_Record is the class that generates A and AAAA records."""
    IP_TYPE_CHOICES = ( ('4','ipv4'),('6','ipv6') )
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=False)
    ip_type         = models.CharField(max_length=1, choices=IP_TYPE_CHOICES, editable=False)

    def __str__(self):
        if self.ip_type == '4':
            record_type = 'A'
        else:
            record_type = 'AAAA'
        return "%s %s %s" % ( self.__fqdn__(), record_type, self.ip.__str__() )

    def __fqdn__(self):
        if self.name == '':
            fqdn = self.domain.name
        else:
            fqdn = self.name+"."+self.domain.name
        return fqdn

    def __repr__(self):
        return "<Address Record '%s'>" % (self.__str__())

    class Meta:
        db_table = 'address_record'



def _add_generic_record( name, domain, ip, ip_type ):
    # Does this record exists?
    _validate_label( name ) #Runs sanity checks. It will raise exceptions if the fqdn is not valid.
    if ip_type == '4':
        ip = add_str_ipv4( ip ) # This runs sanity checks on the ip.
    else:
        ip = add_str_ipv6( ip ) # This runs sanity checks on the ip.

    exist = Address_Record.objects.filter( name = name, domain = domain, ip_type = ip_type ).select_related('ip')
    for possible in exist:
        if possible.ip.__str__() == ip.__str__():
            raise RecordExistsError(possible.__str__()+" already exists.")

    if name == '':
        # Create TLD record
        record = Address_Record( name = name, ip = ip, domain = domain, ip_type = ip_type )
        record.save()
        return record

    fqdn = name+"."+domain.name
    if Domain.objects.filter( name = fqdn ):
        raise InvalidRecordNameError( "You cannot create TLD A record for another domain." )
    record = Address_Record( name = name, ip = ip, domain = domain, ip_type = ip_type )
    record.save()
    return record

def add_A_record( name, domain, ip ):
    """Create an A address record for the full qualified domain name, name + domain.

        :param name: The name to prepended to Domain.name
        :type name: str
        :param domain: Domain the name should exists in.
        :type domain: str
        :param ip: The ip the A record should point to.
        :type ip: str
        :returns: address_record instance that was created.
        :raises: InvalidRecordNameError, CyAddressValueError, ReverseDomainNotFoundError

        note::
            If you are attemping to create a TLD record, pass name=''
            Check ``ip.add_str_ipv4`` for exceptions that might be thrown if **ip** is invalid.

    """
    try:
        ip = ipaddr.IPv4Address(str(ip)).__str__()
    except ipaddr.AddressValueError, e:
        raise CyAddressValueError("Invalid ip %s for IPv%s." % (ip, '4') )

    return _add_generic_record( name, domain, ip, '4' )


def add_AAAA_record( name, domain, ip ):
    """Create an AAAA address record for the full qualified domain name, name + domain.

        :param name: The name to prepended to Domain.name
        :type name: str
        :param domain: Domain the name should exists in.
        :type domain: str
        :param ip: The ip the AAAA record should point to.
        :type ip: str
        :returns: new address_record instance
        :raises: InvalidRecordNameError, CyAddressValueError, ReverseDomainNotFoundError
    """
    try:
        ip = ipaddr.IPv6Address(str(ip)).__str__()
    except ipaddr.AddressValueError, e:
        raise CyAddressValueError("Invalid ip %s for IPv%s." % (ip, '6') )
    return _add_generic_record( name, domain, ip, '6' )

def _remove_generic_record( name, domain, ip, ip_type ):
    if not domain or not ip or ( name != '' and not name ):
        raise RecordNotFoundError("Error: name, domain, and ip are required")

    if name == '':
        fqdn = domain.name
    else:
        fqdn = name+"."+domain.name

    _validate_name( fqdn )

    try:
        if ip_type == '4':
            ip_upper, ip_lower = 0, ipaddr.IPv4Address(ip).__int__()
        else:
            ip_upper, ip_lower = ipv6_to_longs(ip)

    except ipaddr.AddressValueError, e:
        raise RecordNotFoundError("Error: The record %s %s %s was not found." % (fqdn,\
                                                'A' if ip_type == '4' else 'AAAA', ip.__str__()) )

    exist = Address_Record.objects.filter( name = name, domain = domain, ip__ip_upper = ip_upper,\
                                           ip__ip_lower = ip_lower, ip_type = ip_type )
    if exist:
        exist[0].ip.delete() #Django is dumb and doesn't cascade delete (O.k., it's not "dumb")
        exist[0].delete()
    else:
        raise RecordNotFoundError("Error: The record %s %s %s was not found." % (fqdn,\
                                                'A' if ip_type == '4' else 'AAAA', ip.__str__()) )


def remove_A_record( name, domain, ip ):
    """Remove an A record.

        :param name: The name to in Domain.name.
        :type name: str
        :param domain: Domain the name exists in.
        :type domain: str
        :param ip: IP of the record to be deleted
        :type ip: str
        :returns: True -- When successful
        :raises: RecordNotFoundError
    """
    return _remove_generic_record( name, domain, str(ip), '4' )


def remove_AAAA_record( name, domain, ip ):
    """Remove an AAAA record.

        :param name: The name in Domain.name
        :type name: str
        :param domain: Domain the name should exists in.
        :type domain: str
        :param ip: IP of the record to be deleted
        :type ip: str
        :returns: True -- When successful
        :raises: RecordNotFoundError
    """
    return _remove_generic_record( name, domain, str(ip), '6' )

def _update_generic_record( address_record, new_name, new_ip, ip_type ):
    # Make sure we have enough information to even update something.
    if not address_record:
        raise RecordNotFoundError("Error: address_record required")
    if not new_name and not new_ip:
        raise InvalidRecordNameError("Error: A new_name or new_ip is required for updating a address record.")
    if new_name or new_name == '':
        fqdn = str(new_name)+"."+address_record.domain.name
    else:
        fqdn = address_record.__fqdn__()

    # Validate the new_ip if there is one.
    if new_ip:
        if type(new_ip) is not type(''):
            raise CyAddressValueError("Error: %s is not type 'str'." % (new_ip) )
        new_ip = new_ip.lower()
        exist = Address_Record.objects.filter( name = new_name, domain = address_record.domain, ip_type = ip_type ).select_related('ip')
        if exist and exist[0].ip.__str__() == new_ip:
            raise RecordExistsError("Error: The record %s already exists." % (exist.__str__()) )
        try:
            if ip_type == '4':
                ip = add_str_ipv4( new_ip ) # This runs sanity checks on the ip.
            else:
                ip = add_str_ipv6( new_ip ) # This runs sanity checks on the ip.

        except ipaddr.AddressValueError, e:
            raise CyAddressValueError("Error: %s is not a valid IPv%s address." % (new_ip, ip_type) )

    # Validate the new_name if there is one.
    if new_name or new_name == '':
        _validate_label( new_name ) # Will throw errors if new_name is invalid
        if Domain.objects.filter( name = fqdn ):
            raise InvalidRecordNameError( "You cannot create a TLD A record for another domain." )

    # Everything is valid. Update.
    if new_ip:
        old_ip = address_record.ip
        address_record.ip = ip
        # Race conditions?
        address_record.ip.save()
    if new_name:
        address_record.name = new_name
        # Race conditions?
    if new_ip or new_name:
        address_record.save()


def update_A_record( A_record, new_name=None, new_ip=None ):
    """Update an A record with a new_name AND/OR new_ip

        :param new_name: The new name of the A record.
        :type new_name: str
        :param ip_name: The new ip of the A record.
        :type ip_name: str
        :returns: True -- When successful
        :raises:
    """
    return _update_generic_record( A_record, new_name, new_ip, '4' )

def update_AAAA_record( A_record, new_name=None, new_ip=None ):
    """Update an AAAA record with a new_name AND/OR new_ip

        :param new_name: The new name of the AAAA record.
        :type new_name: str
        :param ip_name: The new ip of the AAAA record.
        :type ip_name: str
        :returns: True -- When successful
        :raises:
    """
    return _update_generic_record( A_record, new_name, new_ip, '6' )
