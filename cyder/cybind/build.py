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
from jinja2 import Environment, PackageLoader
import pdb

env = Environment(loader=PackageLoader('cyder.cybind', 'templates'))

soa_template = env.get_template("soa.jinja2")
domain_template = env.get_template("domain.jinja2")
BIND_PATH = "/nfs/milo/u1/uberj/cyder_env/cyder/cyder/cybind/build"
DEFAULT_TTL = 999

def walk_tree(domain):
    gen_domain(domain)
    for child_domain in Domain.objects.filter(master_domain = domain):
        walk_tree(child_domain)

def gen_domain(domain):
    """
    Get all objects in a domain and render them in their respected domain file.
    """
    data = domain_template.render(
                            default_ttl=DEFAULT_TTL,\
                            nameserver_set = domain.nameserver_set.all(),\
                            mx_set = domain.mx_set.all(),\
                            addressrecord_set = domain.addressrecord_set.all(),\
                            cname_set = domain.cname_set.all(),\
                            srv_set = domain.srv_set.all(),\
                            txt_set = domain.txt_set.all(),\
                          )
    return data

def find_root_domain(domains):
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

def gen_soa(soa):
    """
    Generate the SOA file along with all of it's $INCLUDE statements.
    """
    # Find the first domain with the soa. This is the root of the zone.
    domains = soa.domain_set.all()
    root_domain = find_root_domain(domains)
    if not root_domain:
        return

    data = soa_template.render(
                                soa=soa, root_domain=root_domain,\
                                domains=domains, bind_path=BIND_PATH,\
                              )
    return data

def quick_update(domain):
    """
    Regenerate the new domain, then regenerate the file with the soa in it to change
    the serials. Finally, send a notify to the slave name servers.

    We may want to consider using a global lock for this function.
    """
    gen_domain(domain)
    gen_soa(domain.soa)

