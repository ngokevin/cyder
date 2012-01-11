from cyder.cydns.soa.models import Soa

def create_new_domain_soa( dname, primary, contact, serial, expire, retry, refresh ):
    pass


def _add_generic_record( domain, record ):
    record.domain = domain

