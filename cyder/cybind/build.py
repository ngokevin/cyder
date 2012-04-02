"""
Each SOA has a corresponding file that contains $INCLUDES of the domain files that are within
the zone the SOA corresponds to. Using includes allows for the easy regeneration of this file
which is usefull for incrimenting the Serial.

The file name is the name in the soa with '.soa' appended. Here is the general structure of the
file::

    file: example.com.soa

        example.com.    IN    SOA   ns.example.com. hostmaster.example.com. (
                                  2003080800 ; sn = serial number
                                  172800     ; ref = refresh = 2d
                                  900        ; ret = update retry = 15m
                                  1209600    ; ex = expiry = 2w
                                  3600       ; min = minimum = 1h
                                  )

        $INCLUDE example.com
        $INCLUDE foo.example.com
        $INCLUDE bar.example.com
        $INCLUDE baz.bar.example.com
        ...
        ...


Each domain has a file containing all of it's record sets. The file name is just the domain name
iteself::

    file: bar.example.com

        [ NS set ]
        [ MX set ]
        [ A set ]
        [ CNAME set]
        ...
        ...
        [ All record sets ]


"""
from cyder.cydns.soa.models import SOA
from cyder.cybind.generators.bind_domain_generator import render_domain
from cyder.cybind.generators.bind_soa_generator import render_soa
from cyder.cybind.generators.bind_reverse_domain_generator import render_reverse_domain

import pdb

BUILD_PATH = "/nfs/milo/u1/uberj/cyder_env/cyder/cyder/cybind/build"
DEFAULT_TTL = 999

# DEBUG OPTIONS
DEBUG = True
DEBUG_BUILD_STRING = '' # A string to store build output in.


def find_reverse_root_domain(reverse_domains):
    """
    It is nessicary to know which reverse domain is at the top of a zone. This function returns
    that domain.
    """
    if not reverse_domains:
        return None
    root_reverse_domain = reverse_domains[0]
    while True:
        if root_reverse_domain is None:
            raise Exception
        elif not root_reverse_domain.master_reverse_domain:
            break
        elif root_reverse_domain.master_reverse_domain.soa != root_reverse_domain.soa:
            break
        else:
            root_reverse_domain = root_reverse_domain.master_reverse_domain

    return root_reverse_domain

def gen_reverse_domain(reverse_domain):
    """
    Get all objects in a reverse_domain and render them in their respected domain file.
    """
    data = render_reverse_domain(
                            default_ttl=DEFAULT_TTL,
                            nameserver_set = reverse_domain.reversenameserver_set.all(),\
                            ptr_set = reverse_domain.ptr_set.all().order_by('ip_upper', 'ip_lower')
                            )
    file_name = reverse_domain.name
    return (file_name, data)

def gen_reverse_soa(soa):
    """
    Generate the SOA file along with all of it's $INCLUDE statements.
    """
    # Find the first domain with the soa. This is the root of the zone.
    reverse_domains = soa.reversedomain_set.all()
    root_reverse_domain = find_reverse_root_domain(reverse_domains)
    if not root_reverse_domain:
        return

    data = render_soa(
                                soa=soa, root_domain=root_reverse_domain,\
                                domains=reverse_domains, bind_path=BUILD_PATH,\
                              )
    file_name = "%s.soa" % (root_reverse_domain.name)
    return (file_name, data)


def build_reverse_zone_files():
    DEBUG_STRING = ''
    for soa in SOA.objects.all():
        info = gen_reverse_soa(soa)
        if not info:
            continue
        open("%s/%s" % (BUILD_PATH, info[0]), "w+").write(info[1])
        if DEBUG: DEBUG_STRING += "%s File: %s %s \n%s\n" % ("="*20, info[0], "="*20, info[1])

        domains_in_zone = soa.reversedomain_set.all()
        for domain in domains_in_zone:
            info = gen_reverse_domain(domain)
            if not info:
                continue
            open("%s/%s" % (BUILD_PATH, info[0]), "w+").write(info[1])
            if DEBUG: DEBUG_STRING += "%s File: %s %s \n%s\n" % ("+"*20, info[0], "+"*20, info[1])
    return DEBUG_STRING



#### Forward Build Functions ####
def find_forward_root_domain(domains):
    """
    It is nessicary to know which domain is at the top of a zone. This function returns
    that domain.
    """
    if not domains:
        return None
    root_domain = domains[0]
    while True:
        if root_domain is None:
            raise Exception
        elif not root_domain.master_domain:
            break
        elif root_domain.master_domain.soa != root_domain.soa:
            break
        else:
            root_domain = root_domain.master_domain

    return root_domain


def gen_domain(domain):
    """
    Get all objects in a domain and render them in their respected domain file.
    """
    data = render_domain(
                            default_ttl=DEFAULT_TTL,
                            nameserver_set = domain.nameserver_set.all().order_by('server'),
                            mx_set = domain.mx_set.all().order_by('server'),
                            addressrecord_set = domain.addressrecord_set.all().order_by('ip_type', 'label'),
                            cname_set = domain.cname_set.all().order_by('label'),
                            srv_set = domain.srv_set.all().order_by('label'),
                            txt_set = domain.txt_set.all().order_by('label'),
                        )
    file_name = domain.name
    return (file_name, data)


def gen_forward_soa(soa):
    """
    Generate the SOA file along with all of it's $INCLUDE statements.
    """
    # Find the first domain with the soa. This is the root of the zone.
    domains = soa.domain_set.all().order_by('name')
    root_domain = find_forward_root_domain(domains)
    if not root_domain:
        return

    data = render_soa(
                        soa=soa, root_domain=root_domain,\
                        domains=domains, bind_path=BUILD_PATH,\
                     )
    file_name = "%s.soa" % (root_domain.name)
    return (file_name, data)

def quick_forward_update(domain):
    """
    Regenerate the new domain, then regenerate the file with the soa in it to change
    the serials. Finally, send a notify to the slave name servers.

    We may want to consider using a global lock for this function.
    """
    gen_domain(domain)
    gen_forward_soa(domain.soa)

def build_forward_zone_files():
    DEBUG_STRING = ''
    for soa in SOA.objects.all():
        info = gen_forward_soa(soa)
        if not info:
            continue
        # Open a file (create if doesn't exist) in build path. Write data to it. Close it.
        open("%s/%s" % (BUILD_PATH, info[0]), "w+").write(info[1])
        if DEBUG: DEBUG_STRING += "%s File: %s %s \n%s\n" % ("="*20, info[0], "="*20, info[1])
        domains_in_zone = soa.domain_set.all()
        for domain in domains_in_zone:
            info = gen_domain(domain)
            open("%s/%s" % (BUILD_PATH, info[0]), "w+").write(info[1])
            if DEBUG: DEBUG_STRING += "%s File: %s %s \n%s\n" % ("+"*20, info[0], "+"*20, info[1])
    return DEBUG_STRING


def build_dns(*args, **kwargs):
    build_forward_zone_files()
    build_reverse_zone_files()
