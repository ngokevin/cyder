from django.db import models
from cyder.cydns.soa.models import SOA
from cyder.settings.local import CYDNS_BASE_URL
from cyder.cydns.cydns import _validate_name, InvalidRecordNameError
from django.views.decorators.csrf import csrf_exempt

from django.forms import ValidationError
from django import forms
import pdb


class Domain( models.Model ):
    """A Domain is used for most DNS records."""
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    master_domain   = models.ForeignKey("self", null=True, default=None, blank=True)
    soa             = models.ForeignKey(SOA, null=True, default=None, blank=True)

    def __init__(self, *args, **kwargs):
        super(Domain, self).__init__(*args, **kwargs)

    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/domain/%s/detail" % (self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/domain/%s/update" % (self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/domain/%s/delete" % (self.pk)

    def delete(self, *args, **kwargs):
        _check_for_children( self )
        super(Domain, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(Domain, self).save(*args, **kwargs)

    def clean( self ):
        _validate_name( self.name )
        possible = Domain.objects.filter( name = self.name )
        if possible and possible[0].pk != self.pk:
            raise DomainExistsError("The %s domain already exists." % (self.name))

        self.master_domain = _name_to_master_domain( self.name )

    def __str__(self):
        return "<Domain '%s'>" % (self.name)
    def __repr__(self):
        return  self.__str__()

    class Meta:
        db_table = 'domain'


def _check_for_children( domain ):
    if Domain.objects.filter( master_domain = domain ):
        raise DomainHasChildDomains("Before deleting this domain, please remove it's children.")
    pass

class DomainNotFoundError(ValidationError):
    """This exception is thrown when an attempt is made to reference a domain that doesn't exist."""

class DomainExistsError(ValidationError):
    """This exception is thrown when an attempt is made to create a domain that already exists."""
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

def _name_to_master_domain( dname ):
    """Given an domain name, this function returns the appropriate master domain.

    :param dname: The domain for which we are using to search for a master domain.
    :type dname: str
    :returns: domain -- Domain object
    :raises: MasterDomainNotFoundError
    """
    tokens = dname.split('.')
    master_domain = None
    for i in reversed(range(len(tokens)-1)):
        parent_dname = '.'.join(tokens[i+1:])
        possible_master_domain = Domain.objects.filter( name = parent_dname )
        if not possible_master_domain:
            raise MasterDomainNotFoundError("Master Domain for domain %s, not found." % (dname))
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

