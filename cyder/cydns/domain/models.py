from django.db import models
from cyder.cydns.soa.models import Soa
import pdb

class Domain( models.Model ):
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    master_domain   = models.ForeignKey("self", null=True)
    soa             = models.ForeignKey(Soa, null=True)

    class Meta:
        db_table = 'domain'

class DomainNotFoundError(Exception):
    def __str__(self):
        return "No domain found. Condisder creating one."
class DomainExistsError(Exception):
    def __str__(self):
        return "Domain already exists."
class MasterDomainNotFoundError(Exception):
    def __str__(self):
        return "Master domain not found. Please create it."
class DomainHasChildDomains(Exception):
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
    tokens = dname.split('.')
    master_domain = None
    for i in reversed(range(len(tokens)-1)):
        parent_dname = '.'.join(tokens[i+1:])
        master_domain = Domain.objects.filter( name = parent_dname )
        if not master_domain:
            raise MasterDomainNotFoundError
    return master_domain


"""
Given a dname make sure that it does not have any childern. If it does have children return the child.
dname: <'str'>
"""
def remove_domain_str( dname ):
    domain = Domain.objects.filter( name = dname )
    if not domain:
        raise DomainNotFoundError
    remove_domain( domain[0] )

"""
Exact same as remove_domain_str except it uses an object instead of a string.
domain: <domain object>
"""
def remove_domain( domain ):
    if not domain:
        raise DomainNotFoundError
    if Domain.objects.filter( master_domain = domain ):
        raise DomainHasChildDomains
    else:
        domain.delete()

"""
dname: <'str'>
master_domain: <domain_object>
defualt_soa: <soa_object>

Rules for creating a new domain:
    1) The master domain has to exist.
        I.E. Say we want to create oregonstate.edu. The 'edu' domain has to exists first.
        If you ask to create a domain 'dname' and it doesn't have a valid master domain, a
        MasterDomainNotFoundError *will* be thrown.
    2) A DomainExistsError *will* be thrown if you try to add a domain that exists.

defualt_soa: This can be used to create a new domain and automatically create an soa for it.
Subsiquent domains that are added will then inherite that soa. This can also be done manually.
"""
def add_domain( dname, master_domain, defualt_soa=None ):
    if master_domain is None:
        soa = defualt_soa
    else:
        soa = master_domain.soa

    _dname_to_master_domain( dname ) # This function runs sanity checks
    if Domain.objects.filter( name = dname ):
        raise DomainExistsError
    domain = Domain( name=dname, master_domain=master_domain, soa=soa )
    domain.save()
    return domain
