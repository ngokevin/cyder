from django.db import models
from cyder.cydns.soa.models import Soa
import pdb

class Domain( models.Model ):
    """A Domain is used to most DNS records."""
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    master_domain   = models.ForeignKey("self", null=True)
    soa             = models.ForeignKey(Soa, null=True, default=None)

    def __str__(self):
        return "<Domain '%s'>" % (self.name)
    def __repr__(self):
        return  self.__str__()

    class Meta:
        db_table = 'domain'

class DomainNotFoundError(Exception):
    """This exception is thrown when an attempt is made to reference a domain that doesn't exist."""
    def __str__(self):
        return "No domain found. Condisder creating one."
class DomainExistsError(Exception):
    """This exception is thrown when an attempt is made to create a domain that already exists."""
    def __str__(self):
        return "Domain already exists."
class MasterDomainNotFoundError(Exception):
    """This exception is thrown when an attempt is made to add a domain that doesn't have a valid master domain."""
    def __str__(self):
        return "Master domain not found. Please create it."
class DomainHasChildDomains(Exception):
    """This exception is thrown when an attempt is made to delete a domain that has children domains."""
    def __str__(self):
        return "Domain has child domains."

"""
Given an name return the most specific domain that the ip can belong to.
This is used to check for rule 1 in add_domain() rules.
@param: name
@return: domain

A name x.y.z can be split up into x y and z. The domains, 'y.z' and 'z' shoud exist.
@return master_domain if valid domain
        None if invalid master domain
"""

def _dname_to_master_domain( dname ):
    """Given an domain name, this function returns the appropriate master domain.

    :param dname: The domain for which we are using to search for a master domain.
    :type dname: str
    :returns: domain -- Domain object
    :raises: MasterDomainNotFoundError
    """
    dname = dname.rstrip('.')
    tokens = dname.split('.')
    master_domain = None
    for i in reversed(range(len(tokens)-1)):
        parent_dname = '.'.join(tokens[i+1:])
        possible_master_domain = Domain.objects.filter( name = parent_dname )
        if not possible_master_domain:
            raise MasterDomainNotFoundError
        else:
            master_domain = possible_master_domain[0]
    return master_domain

def remove_domain_str( dname ):
    """Given a dname make sure that it does not have any childern.

    :param dname: The domain to remove.
    :type dname: str
    :returns: bool -- True on success
    :raises: DomainNotFoundError
    """
    domain = Domain.objects.filter( name = dname )
    if not domain:
        raise DomainNotFoundError
    remove_domain( domain[0] )
    return True

def remove_domain( domain ):
    """Exact same as remove_domain_str except it uses an object instead of a string.

        :param dname: The domain to remove.
        :type dname: str
        :returns: bool -- True on success
        :raises: DomainNotFoundError, DomainHasChildDomains
    """
    if not domain:
        raise DomainNotFoundError
    if Domain.objects.filter( master_domain = domain ):
        raise DomainHasChildDomains
    else:
        domain.delete()
        return True

def add_domain( dname, default_soa=None ):
    """Create a domain **dname** and attach the correct master domain.

        :param dname: The domain name to add.
        :type dname: str
        :param defualt_soa: An optional feild to tag a domain with a different Soa than it's master domain.
        :returns: bool -- True on success
        :raises: DomainExistsError

        note::
            Rules for creating a new domain:
                1) The master domain has to exist.
                    I.E. Say we want to create oregonstate.edu. The 'edu' domain has to exists first.
                    If you ask to create a domain 'dname' and it doesn't have a valid master domain, a
                    MasterDomainNotFoundError *will* be thrown.
                2) A DomainExistsError *will* be thrown if you try to add a domain that exists.
    """
    if Domain.objects.filter( name = dname ):
        raise DomainExistsError

    master_domain = _dname_to_master_domain( dname )

    if master_domain is None or default_soa is not None:
        soa = default_soa
    else:
        soa = master_domain.soa

    domain = Domain( name=dname, master_domain=master_domain, soa=soa )
    domain.save()
    return domain
