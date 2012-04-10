import cyder


def fqdn_search(fqdn, *args, **kwargs):
    """Find any records that have a name that is the provided fqdn. This
    name would show up on the left hand side of a zone file and in a PTR's
    case the right side.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: (type, Querysets) tuples containing all the objects that matched during
    the search are returned.
    """
    return _build_queries(fqdn, *args, **kwargs)


def fqdn_exists(fqdn, **kwargs):
    """Return a Queryset or False depending on whether an object exists
    with the fqdn.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: True or False
    """
    for type_, qset in _build_queries(fqdn, **kwargs):
        if qset.exists():
            return qset
    return False

def ip_search(ip_str):
    qsets = []
    qsets.append(('AddressRecord', cyder.cydns.address_record.models.AddressRecord.objects.
                    filter(ip_str=ip_str)))
    qsets.append(('PTR', cyder.cydns.ptr.models.PTR.objects.
                    filter(ip_str=ip_str)))
    return qsets

def _build_queries(fqdn, dn=True, rn=True, mx=True, sr=True, tx=True,
                    cn=True, ar=True, pt=True, ip=False):
    # We import this way to make it easier to import this file without
    # getting cyclic imports.
    qsets = []
    if dn:
        qsets.append(('Domain', cyder.cydns.domain.models.Domain.objects.
                        filter(name=fqdn)))
    if rn:
        qsets.append(('ReverseDomain', cyder.cydns.reverse_domain.models.
            ReverseDomain.objects.filter(name=fqdn)))
    if mx:
        qsets.append(('MX', cyder.cydns.mx.models.MX.objects.
                        filter(fqdn=fqdn)))
    if sr:
        qsets.append(('SRV', cyder.cydns.srv.models.SRV.objects.
                        filter(fqdn=fqdn)))
    if tx:
        qsets.append(('TXT', cyder.cydns.txt.models.TXT.objects.
                        filter(fqdn=fqdn)))
    if cn:
        qsets.append(('CNAME', cyder.cydns.cname.models.CNAME.objects.
                        filter(fqdn=fqdn)))
    if ar:
        qsets.append(('AddressRecord', cyder.cydns.address_record.models.AddressRecord.objects.
                        filter(fqdn=fqdn)))
    if pt:
        qsets.append(('PTR', cyder.cydns.ptr.models.PTR.objects.
                        filter(name=fqdn)))

    return qsets
