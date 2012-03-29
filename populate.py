from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.soa.models import SOA
from cyder.cydns.ptr.models import PTR
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.cname.models import CNAME
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.tests.view_tests import random_label

import random
import pdb

def random_ipv4( base_ip ):
    split = base_ip.split('.')
    for i in range(0,4-len(split)):
        base_ip += "."+str(random.randint(0,255))
    return base_ip

domains = (
        "foo",
        "bar.foo",
        "foo.foo",
        "foo.foo.foo",
        "baz.bar.foo",
        )

OSU_BLOCK = "1234:123:"
a_recs = (
        ('', random_ipv4('128.193'), '4'),
        ('pizza', random_ipv4('128.193'), '4'),
        ('noob', random_ipv4('128.193'), '4'),
        ('derp', random_ipv4('128.193'), '4'),
        ('herp', random_ipv4('128.193'), '4'),
        ('', OSU_BLOCK+':1', '6'),
        ('pizza', OSU_BLOCK+':2', '6'),
        ('noob', OSU_BLOCK+':3', '6'),
        ('derp',OSU_BLOCK+':4', '6'),
        ('herp',OSU_BLOCK+':4', '6'),
        )


s,_ = SOA.objects.get_or_create( primary = "ns1.bar.foo", contact="hostmaster.bar.foo" , comment="SOA for bar.foo zone")
s1,_ = SOA.objects.get_or_create( primary = "ns1.foo.foo", contact="hostmaster.bar.foo" , comment="SOA for foo.foo zone")
for domain in domains:
    Domain.objects.get_or_create(name=domain)

for domain in [ domain for domain in domains if domain.find('bar.foo') > -1 ]:
    d, _ = Domain.objects.get_or_create(name=domain)
    d.soa = s
    d.save()

for domain in [ domain for domain in domains if domain.find('foo.foo') > -1 ]:
    d, _ = Domain.objects.get_or_create(name=domain)
    d.soa = s1
    d.save()

d, _=Domain.objects.get_or_create(name=domains[1]) # bar.foo

for a_rec in a_recs:
    AddressRecord.objects.get_or_create( label = a_rec[0], domain=d, ip_str=a_rec[1], ip_type=a_rec[2])

d, _=Domain.objects.get_or_create(name=domains[2]) # foo.foo
# Address Record
for i in range(100):
    AddressRecord.objects.get_or_create( label = random_label(), domain=d, ip_str=a_recs[1][1], ip_type=a_recs[1][2])

label = "derp"
domain = d
data = "foo.com"
cn, _ = CNAME.objects.get_or_create( label = label, domain = domain, data = data )

# Reverse stuff
s,_ = SOA.objects.get_or_create( primary = "ns1.bar.foo", contact="hostmaster.bar.foo" , comment="SOA for the 128.193 zone")
s1,_ = SOA.objects.get_or_create( primary = "ns1.bar.foo", contact="hostmaster.bar.foo" , comment="SOA for the 128.193.15 zone")
r, _ = ReverseDomain.objects.get_or_create(name='128')

r, _ = ReverseDomain.objects.get_or_create(name='128.193')
r.soa = s
r.save()

r1, _ = ReverseDomain.objects.get_or_create(name='128.193.15')
r1.soa = s1
r1.save()

for i in range(0, 100):
    PTR.objects.get_or_create( name = random_label(), ip_str= random_ipv4('128.193'), ip_type = '4')

for i in range(0, 100):
    PTR.objects.get_or_create( name = random_label(), ip_str= random_ipv4('128.193.15'), ip_type = '4')
