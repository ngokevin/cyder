from django.db import models
from django.core.exceptions import ValidationError

import string
import pdb
"""
.. module:: cydns

"""

"""
CyAddressValueError
    This exception is thrown when an attempt is made to create/update a record with an invlaid IP.

InvalidRecordNameError
    This exception is thrown when an attempt is made to create/update a record with an invlaid name.

RecordExistsError
    This exception is thrown when an attempt is made to create a record that already exists.
    All records that can support the unique_together constraint do so. These models will raise
    an IntegretyError. Some models, ones that have to span foreign keys to check for uniqueness,
    need to still raise ValidationError. RecordExistsError will be raised in these cases.

An AddressRecord is an example of a model that raises this Exception.
"""

def _validate_label(label, valid_chars=None):
    """Run test on a record to make sure that the new name is constructed with valid syntax.

        :param label: The name to be tested.
        :type label: str
    """
    _name_type_check(label)

    if not valid_chars:
        valid_chars = string.ascii_letters+"0123456789"+"-"
    for char in label:
        if char == '.':
            raise ValidationError("Error: Ivalid name %s . Please do not span multiple domains when creating A records." % (label))
        if valid_chars.find(char) < 0:
            raise ValidationError("Error: Ivalid name %s . Character '%s' is invalid." % (label, char))
    return

def _validate_domain_name(name):
    """Domain names are different. They are allowed to have '_' in them.

        :param name: The domain name to be tested.
        :type name: str
    """
    _name_type_check(name)

    for label in name.split('.'):
        if not label:
            raise ValidationError("Error: Ivalid name %s . Empty label." % (label))
        valid_chars = string.ascii_letters+"0123456789"+"-_"
        _validate_label(label, valid_chars=valid_chars)

def _validate_name(fqdn):
    """Run test on a name to make sure that the new name is constructed with valid syntax.

        :param fqdn: The fqdn to be tested.
        :type fqdn: str

        note::
            DNS name grammar
            <domain> ::= <subdomain> | " "

            <subdomain> ::= <label> | <subdomain> "." <label>

            <label> ::= <letter> [ [ <ldh-str> ] <let-dig> ]

            <ldh-str> ::= <let-dig-hyp> | <let-dig-hyp> <ldh-str>

            <let-dig-hyp> ::= <let-dig> | "-"

            <let-dig> ::= <letter> | <digit>

            <letter> ::= any one of the 52 alphabetic characters A through Z in
            upper case and a through z in lower case

            <digit> ::= any one of the ten digits 0 through 9
            RFC 1034 http://www.ietf.org/rfc/rfc1034.txt
    """
    # TODO, make sure the grammar is followed.
    _name_type_check(fqdn)

    for label in fqdn.split('.'):
        if not label:
            raise ValidationError("Error: Ivalid name %s . Empty label." % (label))
        _validate_label(label)


def _validate_reverse_name(reverse_name, ip_type):
    """Run test on a name to make sure that the new name is constructed with valid syntax.

        :param fqdn: The fqdn to be tested.
        :type fqdn: str
    """
    _name_type_check(reverse_name)

    valid_ipv6 = "0123456789AaBbCcDdEeFf"

    if ip_type == '4' and len(reverse_name.split('.')) > 4:
        raise ValidationError("Error: IPv4 reverse domains should be a maximum of 4 octets")
    if ip_type == '6' and len(reverse_name.split('.')) > 32:
        raise ValidationError("Error: IPv6 reverse domains should be a maximum of 32 nibbles")

    for chunk in reverse_name.split('.'):
        try:
            if ip_type == '6':
                if valid_ipv6.find(chunk) < 0:
                    raise ValidationError("Error: Ivalid Ipv6 name %s . Character '%s' is invalid." %\
                                                                                    (reverse_name, chunk))
            else:
                if not(int(chunk) <= 255 and int(chunk) >= 0):
                    raise ValidationError("Error: Ivalid Ipv4 name %s . Character '%s' is invalid." %\
                                                                                    (reverse_name, chunk))
        except Exception: #Umm, lol. What am I doing here? TODO Is this exception even needed?
            raise ValidationError("Error: Ivalid Ipv%s name %s." % (ip_type, reverse_name))

def _validate_ttl(ttl):
    if ttl < 0 or ttl > 2147483647: # See RFC 2181
        raise ValidationError("Error: TTLs must be within the 0 to 2147483647 range.")

# Works for labels too.
def _name_type_check(name):
    if type(name) not in (str, unicode):
        raise ValidationError("Error: A name must be of type str.")

