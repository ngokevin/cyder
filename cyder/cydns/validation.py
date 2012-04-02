from django.core.exceptions import ValidationError
import pdb
"""
Both Reverse Domains and Forward Domains have similar functions that need to be called to validate
state in the DB.  Unfortunatly naming convention stops extremely generic code to be written. These
functions are not extremely generic; these functions are sort of generic.

The functions in this file give the name ``domain`` to both ``reverse_domain``s and forward
``domains``s.

"""

def do_zone_validation(domain):
    """
    Preform validation on domain. This function calls the following functions::

        check_for_soa_partition
        check_for_master_delegation
        validate_zone_soa

    .. note::
        The type of the domain that is passed is determined dynamically::

            domain_type = "forward" if type(domain) is Domain else "reverse"

    :param domain: The domain/reverse_domain being validated.
    :type domain: :ref:`domain` or :ref:`reverse_domain`

    The following code is an example of how to call this function during *domain* introspection.

    >>> do_zone_validation(self, self.master_domain)

    The following code is an example of how to call this function during *reverse_domain* introspection.

    >>> do_zone_validation(self, self.master_reverse_domain)

    """
    from cyder.cydns.domain.models import Domain
    domain_type = "forward" if type(domain) is Domain else "reverse"

    if domain_type == 'forward':
        check_for_master_delegation(domain, domain.master_domain)
        validate_zone_soa(domain_type, domain, domain.master_domain)
        check_for_soa_partition(domain, domain.domain_set.all())
    else: # domain_type == 'reverse':
        check_for_master_delegation(domain, domain.master_reverse_domain)
        validate_zone_soa(domain_type, domain, domain.master_reverse_domain)
        check_for_soa_partition(domain, domain.reversedomain_set.all())


def check_for_master_delegation(domain, master_domain):
    """
    No subdomains can be created under a domain that is delegated. This function checks whether a domain
    is violating that condition.

    :param domain: The domain/reverse_domain being validated.
    :type domain: :ref:`domain` or :ref:`reverse_domain`

    :param master_domain: The master domain/reverse_domain of the domain/reverse_domain being validated.
    :type master_domain: :ref:`domain` or :ref:`reverse_domain`

    The following code is an example of how to call this function during *domain* introspection.

    >>> check_for_master_delegation(self, self.master_domain)

    The following code is an example of how to call this function during *reverse_domain* introspection.

    >>> check_for_master_delegation(self, self.master_reverse_domain)

    """
    if not master_domain:
        return
    if not master_domain.delegated:
        return
    if not domain.pk: # We don't exist yet.
        raise ValidationError("No subdomains can be created in the %s domain. It is delegated."\
                % (master_domain.name))

def validate_zone_soa(domain_type, domain, master_domain):
    """
    Make sure the SOA assigned to this domain is the correct SOA for this domain. Also make sure
    that the SOA is not used in a different zone.

    :param domain_type: The type of domain. Either 'reverse' or 'forward'.
    :type domain_type: str

    :param domain: The domain/reverse_domain being validated.
    :type domain: :ref:`domain` or :ref:`reverse_domain`

    :param master_domain: The master domain/reverse_domain of the domain/reverse_domain being validated.
    :type master_domain: :ref:`domain` or :ref:`reverse_domain`

    The following code is an example of how to call this function during *domain* introspection.

    >>> validate_zone_soa('forward', self, self.master_domain)

    The following code is an example of how to call this function during *reverse_domain* introspection.

    >>> validate_zone_soa('reverse', self, self.master_reverse_domain)

    """
    if not domain:
        raise Exception("You called this function wrong")

    if not domain.soa:
        return

    if domain_type == "reverse":
        zone_domains = domain.soa.reversedomain_set.all()
        opposite_zone_domains = domain.soa.domain_set.all()
        root_domain = find_root_domain(domain_type, domain.soa)
    else: # domain_type == "forward"
        zone_domains = domain.soa.domain_set.all()
        opposite_zone_domains = domain.soa.reversedomain_set.all()
        root_domain = find_root_domain(domain_type, domain.soa)

    if opposite_zone_domains.exists():
        raise ValidationError("This SOA is used for the %s zone %s." % (domain_type,\
            opposite_zone_domains[0]))

    if not root_domain: # No one is using this domain.
        return

    if not zone_domains.exists():
        return # No zone uses this soa.

    if master_domain and master_domain.soa != domain.soa:
        # Someone uses this soa, make sure the domain is part of that zone (i.e. has a parent in
        # the zone or is the root domain of the zone).
        if root_domain == domain:
            return
        raise ValidationError("This SOA is used for a different zone.")

def check_for_soa_partition(domain, child_domains):
    """
    This function determines if changing your soa causes sub domains to become their own zones
    and if those zones share a common SOA (not allowed).

    :param domain: The domain/reverse_domain being validated.
    :type domain: :ref:`domain` or :ref:`reverse_domain`

    :param child_domains: A Queryset containing child objects of the :ref:`domain`/:ref:`reverse_domain` object.
    :type child_domains: :ref:`domain` or :ref:`reverse_domain`

    :raises: ValidationError

    The following code is an example of how to call this function during *domain* introspection.

    >>> check_for_soa_partition(self, self.domain_set.all())

    The following code is an example of how to call this function during *reverse_domain* introspection.

    >>> check_for_soa_partition(self, self.reversedomain_set.all())

    """
    for i_domain in child_domains:
        if i_domain.soa == domain.soa:
            continue # Valid child.
        for j_domain in child_domains:
            # Make sure the child domain does not share an SOA with one of it's siblings.
            if i_domain == j_domain:
                continue
            if i_domain.soa == j_domain.soa:
                raise ValidationError("Changing the SOA for the %s domain would cause the child\
                    domains %s and %s to become two zones that share the same SOA. Change %s or\
                    %s's SOA before changing this SOA" % (domain.name, i_domain.name,\
                    j_domain.name, i_domain.name, j_domain.name))

def find_root_domain(domain_type, soa):
    """
    It is nessicary to know which domain is at the top of a zone. This function returns
    that domain.

    :param domain_type: The type of domain. Either 'reverse' or 'forward'.
    :type domain_type: str

    :param soa: A zone's :ref:`soa` object.
    :type soa: :ref:`soa`

    The following code is an example of how to call this function using a Domain as ``domain``.

    >>> find_root_domain('forward', domain.soa)

    The following code is an example of how to call this function using a ReverseDomain as ``domain``.

    >>> find_root_domain('reverse', reverse_domain.soa)

    """
    if domain_type == 'forward':
        return soa.domain_set.all().order_by('name')[:1] # LIMIT 1
    else: # domain_type == 'reverse':
        return soa.reversedomain_set.all().order_by('name')[:1] # LIMIT 1

