from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.mx.models import MX
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.cydns.cname.models import CNAME
from cyder.cydns.address_record.models import AddressRecord

def fqdn_search(fqdn):
    """Find any records that have a name that is the provided fqdn. This name would show up on the
    left hand side of a zone file.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: A Queryset containing all the objects that matched during the search are returned.
    """

def fqdn_exists(fqdn):
    """Return a Queryset or False depending on whether an object exists with the fqdn.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: True or False
    """
    for qset in _build_queries(fqdn):
        if qset.exists():
            return qset
    return False

def _build_queries(fqdn):
    dn = Domain.objects.filter(name=fqdn)
    rn = ReverseDomain.objects.filter(name=fqdn)
    mx = MX.objects.filter(fqdn=fqdn)
    sr = SRV.objects.filter(fqdn=fqdn)
    tx = TXT.objects.filter(fqdn=fqdn)
    cn = CNAME.objects.filter(fqdn=fqdn)
    ar = AddressRecord.objects.filter(fqdn=fqdn)
    return (dn, rn, mx, sr, tx, cn, ar)


