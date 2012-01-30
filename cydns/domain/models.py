from django.db import models
from cyder.cydns.soa.models import SOA
from cyder.cydns.models import _validate_name, InvalidRecordNameError
import pdb

from django.db.models.signals import pre_save, pre_delete


class Domain( models.Model ):
    """A Domain is used for most DNS records."""
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    master_domain   = models.ForeignKey("self", null=True)
    soa             = models.ForeignKey(SOA, null=True, default=None)

    def __init__(self, *args, **kwargs):
        pre_save.connect(validate_domain, sender=self.__class__)
        pre_delete.connect(validate_domain_delete, sender=self.__class__)
        super(Domain, self).__init__(*args, **kwargs)

    def __str__(self):
        return "<Domain '%s'>" % (self.name)
    def __repr__(self):
        return  self.__str__()

    class Meta:
        db_table = 'domain'

def validate_domain(sender, **kwargs):
    domain = kwargs['instance']
    _validate_name( domain.name )
    if Domain.objects.filter( name = domain.name ):
        raise DomainExistsError("The %s domain already exists." % (domain.name))

    master_domain = _dname_to_master_domain( domain.name )
    domain.master_domain = master_domain

def validate_domain_delete(sender, **kwargs):
    if sender.objects.filter( master_domain = kwargs['instance'] ):
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

def _dname_to_master_domain( dname ):
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

def remove_domain_str( dname ):
    """Given a dname make sure that it does not have any childern.

    :param dname: The domain to remove.
    :type dname: str
    :returns: bool -- True on success
    :raises: DomainNotFoundError
    """
    domain = Domain.objects.filter( name = dname )
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
    domain = Domain( name=dname, soa=default_soa )
    domain.save()
    return domain
