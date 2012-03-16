from django.db import models
from django.core.exceptions import ValidationError
from django import forms

from cyder.cydns.soa.models import SOA
from cyder.cydns.cydns import _validate_domain_name, InvalidRecordNameError
from cyder.cydns.models import ObjectUrlMixin

import pdb


class Domain( models.Model, ObjectUrlMixin ):
    """A Domain is used for most DNS records."""
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100, unique=True)
    master_domain   = models.ForeignKey("self", null=True, default=None, blank=True)
    soa             = models.ForeignKey(SOA, null=True, default=None, blank=True)

    def __init__(self, *args, **kwargs):
        super(Domain, self).__init__(*args, **kwargs)

    class Meta:
        db_table = 'domain'

    def delete(self, *args, **kwargs):
        self._check_for_children()
        super(Domain, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(Domain, self).save(*args, **kwargs)

    def clean( self ):
        _validate_domain_name( self.name )
        self.master_domain = _name_to_master_domain( self.name )

    def __str__(self):
        return "%s" % (self.name)
    def __repr__(self):
        return "<Domain '%s'>" % (self.name)



    def _check_for_children( self ):
        if Domain.objects.filter( master_domain = self ):
            raise DomainHasChildDomains("Before deleting this domain, please remove it's children.")
        pass


# A bunch of handy functions that would cause circular dependancies if they were in another file.

class MasterDomainNotFoundError(ValidationError):
    """This exception is thrown when an attempt is made to add a domain that doesn't have a valid master domain."""
class DomainHasChildDomains(ValidationError):
    """This exception is thrown when an attempt is made to delete a domain that has children domains."""

"""
Given an name return the most specific domain that the ip can belong to.
This is used to check for rule 1 in add_domain() rules.
@param: name
@return: domain

A name x.y.z can be split up into x y and z. The domains, 'y.z' and 'z' shoud exist.
@return master_domain if valid domain
        None if invalid master domain
"""

def _name_to_master_domain( name ):
    """Given an domain name, this function returns the appropriate master domain.

    :param name: The domain for which we are using to search for a master domain.
    :type name: str
    :returns: domain -- Domain object
    :raises: MasterDomainNotFoundError
    """
    tokens = name.split('.')
    master_domain = None
    for i in reversed(range(len(tokens)-1)):
        parent_name = '.'.join(tokens[i+1:])
        possible_master_domain = Domain.objects.filter( name = parent_name )
        if not possible_master_domain:
            raise MasterDomainNotFoundError("Master Domain for domain %s, not found." % (name))
        else:
            master_domain = possible_master_domain[0]
    return master_domain

def _name_to_domain( fqdn ):
    labels = fqdn.split('.')
    for i in range(len(labels)):
        name = '.'.join(labels[i:])
        longest_match = Domain.objects.filter( name = name )
        if longest_match:
            return longest_match[0]
    return None


def _check_TLD_condition( record ):
    domain = Domain.objects.filter( name = record.fqdn() )
    if not domain:
        return
    if record.label == '' and domain[0] == record.domain:
        return #This is allowed
    else:
        raise InvalidRecordNameError( "You cannot create an record that points to the top level of another domain." )
