from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import Ip

# This is the A and AAAA record class
class Address_Record( models.Model ):
    """Address_Record is the class that generates A and AAAA records."""
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    ip              = models.OneToOneField(Ip, null=False)
    domain          = models.ForeignKey(Domain, null=False)

    class Meta:
        db_table = 'address_record'

class InvalidRecordNameError(Exception):
    """This exception is thrown when an attempt is made to create/update a record with invlaid information."""
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
    """Run test on a record to make sure that it is a fqdn with valid syntax.

        :param record_name: The name to prepended be tested.
        :type record_name: str
    """
    pass

def add_A_record( name, domain, ip ):
    """Create an A address record for the full qualified domain name, name + domain.

        :param name: The name to prepended to Domain.name
        :type name: str
        :param domain: Domain the name should exists in.
        :type domain: str
        :param ip: The ip the A record should point to.
        :type ip: str
        :returns: address_record instance that was created.
        :raises: InvalidRecordName, AddressValueError, ReverseDomainNotFoundError

        note::
            If you are attemping to create a TLD record, pass name=''
            Check ``ip.add_str_ipv4`` for exceptions that might be thrown if **ip** is invalid.

    """
    if name == '':
        # Create TLD
        ip = add_str_ipv4( ip ) # This runs sanity checks on the ip. It will raise exceptions if the ip is invalid.
        record = Address_Record( name = name, ip = ip, domain = domain )
        return
    fqdn = name+"."+domain.name
    if Domain.objects.filter( name = fqdn ):
        raise InvalidRecordName( "You cannot create TLD A record for another domain." )
    _validate_domain_name( fqdn ) #Runs sanity checks. It will raise exceptions if the fqdn is not valid.
    ip = add_str_ipv4( ip ) # This runs sanity checks on the ip. It will raise exceptions if the ip is invalid.
    record = Address_Record( name = name, ip = ip, domain = domain )


def add_AAAA_record( name, domain, ip ):
    """Create an AAAA address record for the full qualified domain name, name + domain.

        :param name: The name to prepended to Domain.name
        :type name: str
        :param domain: Domain the name should exists in.
        :type domain: str
        :param ip: The ip the AAAA record should point to.
        :type ip: str
        :returns: new address_record instance
        :raises:
    """
    pass


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
