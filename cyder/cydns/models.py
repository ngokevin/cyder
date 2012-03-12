from django.db import models
from django.forms import ValidationError
import string
import pdb
#"""
#q.. module:: cydns
#q
#q"""
#TODO Subclass these Exceptions!
#qclass CyAddressValueError(ValidationError):
    #q"""This exception is thrown when an attempt is made to create/update a record with an invlaid IP."""
#q
#qclass InvalidRecordNameError(ValidationError):
    #q"""This exception is thrown when an attempt is made to create/update a record with an invlaid name."""
#q
#qclass RecordExistsError(ValidationError):
    #q"""This exception is thrown when an attempt is made to create a record that already exists."""
#q
#qclass RecordNotFoundError(ValidationError):
    #q"""This exception is thrown when an attempt is made to remove/update a record that does not       exists."""
    #qdef __init__(self, msg ):
        #q"""Record Not Found ValidationError.
        #q"""
        #qself.msg = msg
    #qdef __str__(self):
        #qreturn self.__repr__()
    #qdef __repr__(self):
        #qreturn self.msg
#q
#q
#qdef _validate_label( label, valid_chars=None ):
    #q"""Run test on a record to make sure that the new name is constructed with valid syntax.
#q
        #q:param label: The name to be tested.
        #q:type label: str
    #q"""
    #qif type(label) not in ( str, unicode ):
            #qraise InvalidRecordNameError("Error: The supplied name '%s' is not of type 'str'." % (label) )
    #qif not valid_chars:
        #qvalid_chars = string.ascii_letters+"0123456789"+"-"
    #qfor char in label:
        #qif char == '.':
            #qraise InvalidRecordNameError("Error: Ivalid name %s . Please do not span multiple domains when creating A records." % (label) )
        #qif valid_chars.find(char) < 0:
            #qraise InvalidRecordNameError("Error: Ivalid name %s . Character '%s' is invalid." % (label, char) )
    #qreturn
#q
#qdef _validate_domain_name( dname ):
    #q"""Domain names are different. They are allowed to have '_' in them.
#q
        #q:param dname: The domain name to be tested.
        #q:type dname: str
    #q"""
    #qif type(dname) not in ( str, unicode ):
        #qraise InvalidRecordNameError("Error: Ivalid name %s. Not of type str." % (dname) )
#q
    #qfor label in dname.split('.'):
        #qif not label:
            #qraise InvalidRecordNameError("Error: Ivalid name %s . Empty label." % (label) )
        #qvalid_chars = string.ascii_letters+"0123456789"+"-_"
        #q_validate_label( label, valid_chars=valid_chars )
#q
#qdef _validate_name( fqdn ):
    #q"""Run test on a name to make sure that the new name is constructed with valid syntax.
#q
        #q:param fqdn: The fqdn to be tested.
        #q:type fqdn: str
    #q"""
    #qif type(fqdn) not in ( str, unicode ):
        #qraise InvalidRecordNameError("Error: Ivalid name %s. Not of type str." % (fqdn) )
#q
    #qfor label in fqdn.split('.'):
        #qif not label:
            #qraise InvalidRecordNameError("Error: Ivalid name %s . Empty label." % (label) )
        #q_validate_label( label )
#q
#q
#qdef _validate_reverse_name( reverse_name, ip_type ):
    #q"""Run test on a name to make sure that the new name is constructed with valid syntax.
#q
        #q:param fqdn: The fqdn to be tested.
        #q:type fqdn: str
    #q"""
    #qif type(reverse_name) not in ( str, unicode ):
        #qraise InvalidRecordNameError("Error: Ivalid name %s. Not of type str." % (reverse_name) )
#q
    #qvalid_ipv6 = "0123456789AaBbCcDdEeFf"
#q
    #qif ip_type == '4' and len(reverse_name.split('.')) > 4:
        #qraise InvalidRecordNameError("Error: IPv4 reverse domains should be a maximum of 4 octets")
    #qif ip_type == '6' and len(reverse_name.split('.')) > 32:
        #qraise InvalidRecordNameError("Error: IPv6 reverse domains should be a maximum of 32 nibbles")
#q
    #qfor chunk in reverse_name.split('.'):
        #qtry:
            #qif ip_type == '6':
                #qif valid_ipv6.find(chunk) < 0:
                    #qraise InvalidRecordNameError("Error: Ivalid Ipv6 name %s . Character '%s' is invalid." %\
                                                                                    #q(reverse_name, chunk) )
            #qelse:
                #qif not( int(chunk) <= 255 and int(chunk) >= 0):
                    #qraise InvalidRecordNameError("Error: Ivalid Ipv4 name %s . Character '%s' is invalid." %\
                                                                                    #q(reverse_name, chunk) )
        #qexcept Exception: #Umm, lol. What am I doing here? TODO Is this exception even needed?
            #qraise InvalidRecordNameError("Error: Ivalid Ipv%s name %s." % (ip_type, reverse_name) )
#q
#qdef do_generic_invalid( obj, data, exception, function ):
    #qe = None
    #qtry:
        #qfunction(**data)
    #qexcept exception, e:
        #qpass
    #qobj.assertEqual(exception, type(e))
#q
#qdef _validate_ttl( ttl ):
    #qif ttl < 0 or ttl > 2147483647: # See RFC 2181
        #qraise InvalidRecordNameError("Error: TTLs must be within the 0 to 2147483647 range.")
