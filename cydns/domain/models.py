from django.db import models
from cyder.cydns.soa.models import SOA
from cyder.cydns.models import _validate_name, InvalidRecordNameError
from django.views.decorators.csrf import csrf_exempt

from django.forms import ModelForm
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

    def delete(self, *args, **kwargs):
        _check_for_children( self )
        super(Domain, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(Domain, self).save(*args, **kwargs)

    def clean( self ):
        _validate_domain( self )

    def __str__(self):
        return "<Domain '%s'>" % (self.name)
    def __repr__(self):
        return  self.__str__()

    class Meta:
        db_table = 'domain'

class DomainUpdateForm( ModelForm ):
    class Meta:
        model   = Domain
        exclude = ('name','master_domain',)

class DomainForm( ModelForm ):
    choices = ( (1,'Yes'),
                (0,'No'),
              )
    inherit_soa = forms.ChoiceField(widget=forms.RadioSelect, choices=choices)
    class Meta:
        model   = Domain
        exclude = ('master_domain',)

def _validate_domain( domain ):
    _validate_name( domain.name )
    possible = Domain.objects.filter( name = domain.name )
    if possible and possible[0].pk != domain.pk:
        raise DomainExistsError("The %s domain already exists." % (domain.name))

    domain.master_domain = _name_to_master_domain( domain.name )

def _check_for_children( domain ):
    if Domain.objects.filter( master_domain = domain ):
        raise DomainHasChildDomains("Before deleting this domain, please remove it's children.")
    pass

# TODO subclass these exceptions.
class DomainNotFoundError(Exception):
    """This exception is thrown when an attempt is made to reference a domain that doesn't exist."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class DomainExistsError(Exception):
    """This exception is thrown when an attempt is made to create a domain that already exists."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
class MasterDomainNotFoundError(Exception):
    """This exception is thrown when an attempt is made to add a domain that doesn't have a valid master domain."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
class DomainHasChildDomains(Exception):
    """This exception is thrown when an attempt is made to delete a domain that has children domains."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

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

