"""
Each SOA has a corresponding file that contains $INCLUDES of the domain files that are within the
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
iteself.

    file: bar.example.com

        [ NS set ]
        [ MX set ]
        [ A set ]
        [ CNAME set]
        ...
        ...
        [ All record sets ]


"""

def walk_tree(domain):
    gen_domain(domain)
    for child_domain in Domain.objects.filter(master_domain = domain)
        walk_tree(child_domain)

def gen_domain(domain):
    """
    domain_template.render( nameserver_set = domain.nameserver_set.all(),\
                            mx_set = domain.mx_set.all(),\
                            addressrecord_set = domain.addressrecord_set.all(),\
                            cname_set = domain.cname_set.all(),\
                            srv_set = domain.srv_set.all(),\
                            txt_set = domain.txt_set.all(),\
                          )
    """

def gen_soa(soa):
    """
    soa_template.render(soa=soa, domains=soa.domain_set)
    """

def quick_update(domain):
    """
    Regenerate the new domain, then regenerate the file with the soa in it to change
    the serials. Finally, send a notify to the slave name servers.

    We may want to consider using a global lock for this this function.
    """
    gen_domain(domain)
    gen_soa(domain.soa)

