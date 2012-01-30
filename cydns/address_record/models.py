from django.db import models
from cyder.cydns.models import _validate_label, InvalidRecordNameError, CyAddressValueError
from cyder.cydns.models import _validate_name, RecordExistsError, RecordNotFoundError
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip, add_str_ipv4, add_str_ipv6, ipv6_to_longs
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from django.db.models.signals import pre_save, pre_delete, post_delete, post_save
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

    def __init__(self, *args, **kwargs):
        pre_save.connect(validate_record, sender=self.__class__)
        super(Reverse_Domain, self).__init__(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Reverse_Domain, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        name = self.name
        _validate_label( self.name ) #Runs sanity checks. It will raise exceptions if the fqdn is not valid.
        _get_ip( self.ip, self.ip_type )
        _check_exist( self )
        fqdn = _get_fqdn
        _validate_name( fqdn )
        _check_TLD_condition( fqdn )
        super(Reverse_Domain, self).save(*args, **kwargs)

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


def validate_record(sender, **kwargs):
    record = kwargs['instace']
    name = record.name
    _validate_label( name ) #Runs sanity checks. It will raise exceptions if the fqdn is not valid.
    _get_ip( record.ip, record.ip_type )
    _check_exist( record )
    fqdn = _get_fqdn
    _validate_name( fqdn )
    _check_TLD_condition( fqdn )

def _get_ip( name, ip_type ):
    if ip_type == '4':
        ip = add_str_ipv4( ip ) # This runs sanity checks on the ip.
    else:
        ip = add_str_ipv6( ip ) # This runs sanity checks on the ip.

def _check_exist( record ):
    exist = Address_Record.objects.filter( name = record.name, domain = record.domain, ip_type = record.ip_type ).select_related('ip')
    for possible in exist:
        if possible.ip.__str__() == record.ip.__str__() and possible.ip.id != record.ip.id:
            raise RecordExistsError(possible.__str__()+" already exists.")

def _get_fqdn( record ):
    if record.name == '':
        fqdn = record.domain.name
    else:
        fqdn = record.name+"."+record.domain.name

def _check_TLD_condition( fqdn ):
    if Domain.objects.filter( name = fqdn ):
        raise InvalidRecordNameError( "You cannot create TLD A record for another domain." )

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

    # Validate the new_ip if there is one.
    if new_ip:
        if type(new_ip) is not type(''):
            raise CyAddressValueError("Error: %s is not type 'str'." % (new_ip) )
        new_ip = new_ip.lower()
        test_ip = new_ip #Used later for existance checking
        if ip_type == '4':
            ip = add_str_ipv4( new_ip ) # This runs sanity checks on the ip.
        else:
            ip = add_str_ipv6( new_ip ) # This runs sanity checks on the ip.
    else:
        test_ip = address_record.ip.__str__()


    # Validate the new_name if there is one.
    if new_name or new_name == '':
        test_name = new_name #Used later for existance checking
        _validate_label( new_name ) # Will throw errors if new_name is invalid
        if new_name:
            fqdn = str(new_name)+"."+address_record.domain.name
        else:
            fqdn = address_record.domain.name

        if Domain.objects.filter( name = fqdn ):
            raise InvalidRecordNameError( "You cannot create a TLD A record for another domain." )
    else:
        test_name = address_record.name

    #Check to see if this record already exists.
    exist = Address_Record.objects.filter( name = test_name, domain = address_record.domain, ip_type = ip_type ).select_related('ip')
    if exist and exist[0].ip.__str__() == test_ip:
        raise RecordExistsError("Error: The record %s already exists." % (exist.__str__()) )

    # Everything is valid. Update.
    if new_ip:
        old_ip = address_record.ip
        address_record.ip = ip
        # Race conditions?
        address_record.ip.save()
        old_ip.delete()
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
