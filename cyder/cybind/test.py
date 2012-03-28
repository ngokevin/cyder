import sys
import os

sys.path.append("/nfs/milo/u1/uberj/cyder_env/cyder/")
# Edit this if necessary or override the variable in your environment.
os.environ['DJANGO_SETTINGS_MODULE'] = 'cyder.settings'

try:
    # For local development in a virtualenv:
    from funfactory import manage
except ImportError, e:
    # Production:
    # Add a temporary path so that we can import the funfactory
    tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'vendor', 'src', 'funfactory')
    sys.path.append(tmp_path)

    from funfactory import manage

    # Let the path magic happen in setup_environ() !
    sys.path.remove(tmp_path)


manage.setup_environ("/nfs/milo/u1/uberj/cyder_env/cyder/manage.py", more_pythonic=True)
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.soa.models import SOA
from cyder.cydns.ip.models import Ip
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.nameserver.models import Nameserver
from cyder.cybind.build import *

def add_some_records():
    s1, s1_c = SOA.objects.get_or_create(primary = "ns1.foo.gaz", contact = "hostmaster.foo", comment="foo.gaz2")
    s2, s2_c = SOA.objects.get_or_create(primary = "ns1.foo.gaz", contact = "hostmaster.foo", comment="baz.gaz2")
    d, _ = Domain.objects.get_or_create(name="gaz")
    d.soa = None
    d.save()
    d1, _ = Domain.objects.get_or_create(name="foo.gaz")
    if s1_c:
        d1.soa = s1
        d1.save()
    d, _ = Domain.objects.get_or_create(name="baz.foo.gaz")
    if s1_c:
        d.soa = s1
        d.save()
    d, _ = Domain.objects.get_or_create(name="bar.foo.gaz")
    if s1_c:
        d.soa = s1
        d.save()
    d, _ = Domain.objects.get_or_create(name="baz.gaz")
    if s2_c:
        d.soa = s2
        d.save()
    d, _ = Domain.objects.get_or_create(name="gaz.gaz")
    d.soa = None
    d.save()

    _128 , _= ReverseDomain.objects.get_or_create(name='128')

    rs, _ = ReverseNameserver.objects.get_or_create( reverse_domain= _128, server="ns1.foo.com")
    rs.save()
    rs = ReverseNameserver.objects.get_or_create( reverse_domain= _128, server="ns1.foo1.com")
    rs.save()

    test_ip = Ip( ip_str = "128.193.0.1", ip_type = '4' )
    test_ip.save()
    try:
        _, _ = AddressRecord.objects.get_or_create( label = '', domain= d1 , ip = test_ip , ip_type='4')
    except ValidationError:
        pass

    test_ip1 = Ip( ip_str = "128.193.0.1", ip_type = '4' )
    test_ip1.save()
    try:
        _, _ = AddressRecord.objects.get_or_create( label = 'fdjoo',domain= d1 , ip = test_ip1 , ip_type='4')
    except ValidationError:
        pass

    test_ip2 = Ip( ip_str = "128.193.0.1", ip_type = '4' )
    test_ip2.save()
    try:
        _, _ = AddressRecord.objects.get_or_create( label = 'baddr',domain= d1 , ip = test_ip2 , ip_type='4')
    except ValidationError:
        pass

    data = { 'domain':d1 , 'server':'ns2.moot.ru' }
    try:
        _, _ = Nameserver.objects.get_or_create( **data )
    except ValidationError:
        pass

    data = { 'domain':d1 , 'server':'ns3.moot.ru' }
    try:
        _, _ = Nameserver.objects.get_or_create( **data )
    except ValidationError:
        pass



add_some_records()
