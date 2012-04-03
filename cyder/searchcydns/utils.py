import cyder

def fqdn_search(fqdn):
    """Find any records that have a name that is the provided fqdn. This name would show up on the
    left hand side of a zone file.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: A Queryset containing all the objects that matched during the search are returned.
    """

def fqdn_exists(fqdn, **kwargs):
    """Return a Queryset or False depending on whether an object exists with the fqdn.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: True or False
    """
    for qset in _build_queries(fqdn, **kwargs):
        if qset.exists():
            return qset
    return False

def _build_queries(fqdn, dn=True, rn=True, mx=True, sr=True, tx=True,\
                    cn=True, ar=True):
    # We import this way to make it easier to import this file without getting cyclic imports.
    qsets = []
    if dn:
        qsets.append(cyder.cydns.domain.models.Domain.objects.filter(name=fqdn))
    if rn:
        qsets.append(cyder.cydns.reverse_domain.models.ReverseDomain.objects.filter(name=fqdn))
    if mx:
        qsets.append(cyder.cydns.mx.models.MX.objects.filter(fqdn=fqdn))
    if sr:
        qsets.append(cyder.cydns.srv.models.SRV.objects.filter(fqdn=fqdn))
    if tx:
        qsets.append(cyder.cydns.txt.models.TXT.objects.filter(fqdn=fqdn))
    if cn:
        qsets.append(cyder.cydns.cname.models.CNAME.objects.filter(fqdn=fqdn))
    if ar:
        qsets.append(cyder.cydns.address_record.models.AddressRecord.objects.filter(fqdn=fqdn))

    return qsets


