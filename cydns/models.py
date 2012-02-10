from django.db import models
import string
import pdb
"""
.. module:: cydns

"""
#TODO Subclass these Exceptions!
class CyAddressValueError(Exception):
    """This exception is thrown when an attempt is made to create/update a record with an invlaid IP."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

class InvalidRecordNameError(Exception):
    """This exception is thrown when an attempt is made to create/update a record with an invlaid name."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

class RecordExistsError(Exception):
    """This exception is thrown when an attempt is made to create a record that already exists."""
    def __init__(self, msg ):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

class RecordNotFoundError(Exception):
    """This exception is thrown when an attempt is made to remove/update a record that does not       exists."""
    def __init__(self, msg ):
        """Record Not Found Exception.
        """
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg


def _validate_label( label ):
    """Run test on a record to make sure that the new name is constructed with valid syntax.

        :param label: The name to be tested.
        :type label: str
    """
    if type(label) not in ( type(u''), type('') ):
            raise InvalidRecordNameError("Error: The supplied name '%s' is not of type 'str'." % (label) )
    valid_chars = string.ascii_letters+"0123456789"+"-"
    for char in label:
        if char == '.':
            raise InvalidRecordNameError("Error: Ivalid name %s . Please do not span multiple domains when creating A records." % (label) )
        if valid_chars.find(char) < 0:
            raise InvalidRecordNameError("Error: Ivalid name %s . Character '%s' is invalid." % (label, char) )
    return

def _validate_name( fqdn ):
    """Run test on a name to make sure that the new name is constructed with valid syntax.

        :param fqdn: The fqdn to be tested.
        :type fqdn: str
    """
    if type(fqdn) not in ( type(u''), type('') ):
        raise InvalidRecordNameError("Error: Ivalid name %s. Not of type str." % (fqdn) )

    for label in fqdn.split('.'):
        if not label:
            raise InvalidRecordNameError("Error: Ivalid name %s . Empty label." % (label) )
        _validate_label( label )


def _validate_reverse_name( reverse_name, ip_type ):
    """Run test on a name to make sure that the new name is constructed with valid syntax.

        :param fqdn: The fqdn to be tested.
        :type fqdn: str
    """
    if type(reverse_name) != type(u'') and type(reverse_name) != type(''):
        raise InvalidRecordNameError("Error: Ivalid name %s. Not of type str." % (reverse_name) )

    valid_ipv6 = "0123456789AaBbCcDdEeFf"

    if ip_type == '4' and len(reverse_name.split('.')) > 4:
        raise InvalidRecordNameError("Error: IPv4 reverse domains should be a maximum of 4 octets")
    if ip_type == '6' and len(reverse_name.split('.')) > 32:
        raise InvalidRecordNameError("Error: IPv6 reverse domains should be a maximum of 32 nibbles")

    for chunk in reverse_name.split('.'):
        try:
            if ip_type == '6':
                if valid_ipv6.find(chunk) < 0:
                    raise InvalidRecordNameError("Error: Ivalid Ipv6 name %s . Character '%s' is invalid." %\
                                                                                    (reverse_name, chunk) )
            else:
                if not( int(chunk) <= 255 and int(chunk) >= 0):
                    raise InvalidRecordNameError("Error: Ivalid Ipv4 name %s . Character '%s' is invalid." %\
                                                                                    (reverse_name, chunk) )
        except Exception:
            raise InvalidRecordNameError("Error: Ivalid Ipv%s name %s." % (ip_type, reverse_name) )

def do_generic_invalid( obj, data, exception, function ):
    e = None
    try:
        function(**data)
    except exception, e:
        pass
    obj.assertEqual(exception, type(e))

def _validate_ttl( ttl ):
    if ttl < 0 or ttl > 2147483647: # See RFC 2181
        raise InvalidRecordNameError("Error: TTLs must be within the 0 to 2147483647 range.")
