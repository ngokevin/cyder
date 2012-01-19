from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip, add_str_ipv4, add_str_ipv6
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
        if self.name == '':
            fqdn = self.domain.name
        else:
            fqdn = self.name+"."+self.domain.name
        if self.ip_type == '4':
            record_type = 'A'
        else:
            record_type = 'AAAA'
        return "%s %s %s" % ( fqdn, record_type, self.ip.__str__() )

    def __repr__(self):
        return "<Address Record '%s'>" % (self.__str__())

    class Meta:
        db_table = 'address_record'

class InvalidRecordNameError(Exception):
    """This exception is thrown when an attempt is made to create/update a record with an invlaid name."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

class AddressValueError(Exception):
    """This exception is thrown when an attempt is made to create/update a record with an invlaid IP."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

class RecordExistsError(Exception):
    """This exception is thrown when an attempt is made to create a record that already exists."""
    def __init__(self, r_type = 'DNS'):
        """Record allready exists Exception.
        :param r_type: The type of record. Either 'A' or 'AAAA'. By defualt r_type='DNS'.
        :type  r_type: str
        """
        self.msg = "The "+r_type+" record you tried to create already exists."
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

class RecordNotFoundError(Exception):
    """This exception is thrown when an attempt is made to remove/update a record that does not exists."""
    def __init__(self, r_type = 'DNS'):
        """Record allready Not Found Exception.
        :param r_type: The type of record. Either 'A' or 'AAAA'. By defualt r_type='DNS'.
        :type  r_type: str
        """
        self.msg = "The "+r_type+" record you tried to remove does not exist."
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

def _validate_domain_name( record_name ):
    """Run test on a record to make sure that the new name is constructed with valid syntax.

        :param record_name: The name to be tested.
        :type record_name: str
    """
    valid_chars = string.ascii_letters+"0123456789"+"-"
    for char in record_name:
        if char == '.':
            raise InvalidRecordNameError("Error: Ivalid name %s . Please do not span multiple domains when creating A records." % (record_name) )
        if valid_chars.find(char) < 0:
            raise InvalidRecordNameError("Error: Ivalid name %s . Character '%s' is invalid." % (record_name, char) )
    return

def _add_generic_record( name, domain, ip, ip_type ):
    # Does this record exists?
    ip = ip.lower()
    exist = Address_Record.objects.filter( name = name, domain = domain, ip_type = ip_type )
    if exist and exist[0].ip.__str__() == ip:
        raise RecordExistsError(exist[0].__str__()+" already exists.")

    _validate_domain_name( name ) #Runs sanity checks. It will raise exceptions if the fqdn is not valid.
    try:
        if ip_type == '4':
            ip = add_str_ipv4( str(ip) ) # This runs sanity checks on the ip. Raises exceptions if the ip is invalid.
        else:
            ip = add_str_ipv6( str(ip) ) # This runs sanity checks on the ip. Raises exceptions if the ip is invalid.
    except ipaddr.AddressValueError, e:
        raise AddressValueError("Invalid ip %s for IPv%s." % (ip,ip_type) )

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
        :raises: InvalidRecordNameError, AddressValueError, ReverseDomainNotFoundError

        note::
            If you are attemping to create a TLD record, pass name=''
            Check ``ip.add_str_ipv4`` for exceptions that might be thrown if **ip** is invalid.

    """
    if type(ip) != type(''):
        raise AddressValueError("Type %s is not of type 'str'." % (type(ip)))
    return _add_generic_record( name, domain, str(ip), '4' )


def add_AAAA_record( name, domain, ip ):
    """Create an AAAA address record for the full qualified domain name, name + domain.

        :param name: The name to prepended to Domain.name
        :type name: str
        :param domain: Domain the name should exists in.
        :type domain: str
        :param ip: The ip the AAAA record should point to.
        :type ip: str
        :returns: new address_record instance
        :raises: InvalidRecordNameError, AddressValueError, ReverseDomainNotFoundError
    """
    if type(ip) != type(''):
        raise AddressValueError("Type %s is not of type 'str'." % (type(ip)))
    return _add_generic_record( name, domain, ip, '6' )


def remove_A_record( name, domain):
    """Remove an A record.

        :param name: The name to in Domain.name.
        :type name: str
        :param domain: Domain the name exists in.
        :type domain: str
        :returns: True -- When successful
        :raises: RecordNotFoundError
    """
    pass


def remove_AAAA_record( name, domain ):
    """Remove an AAAA record.

        :param name: The name in Domain.name
        :type name: str
        :param domain: Domain the name should exists in.
        :type domain: str
        :returns: True -- When successful
        :raises: RecordNotFoundError
    """
    pass

def update_A_record( A_record, new_name=None, new_ip=None ):
    """Update an A record with a new_name AND/OR new_ip

        :param new_name: The new name of the A record.
        :type new_name: str
        :param ip_name: The new ip of the A record.
        :type ip_name: str
        :returns: True -- When successful
        :raises:
    """
    pass

def update_AAAA_record( A_record, new_name=None, new_ip=None ):
    """Update an AAAA record with a new_name AND/OR new_ip

        :param new_name: The new name of the AAAA record.
        :type new_name: str
        :param ip_name: The new ip of the AAAA record.
        :type ip_name: str
        :returns: True -- When successful
        :raises:
    """
    pass
