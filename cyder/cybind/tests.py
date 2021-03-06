import sys
import os
import pdb

from django.test import TestCase

from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.cydns.ptr.models import PTR
from cyder.cydns.mx.models import MX
from cyder.cydns.cname.models import CNAME
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.nameserver.nameserver.models import Nameserver
from cyder.cydns.nameserver.reverse_nameserver.models import ReverseNameserver
from cyder.cybind.build import *

class BuildTests(TestCase):
    def setUp(self):
        s1, s1_c = SOA.objects.get_or_create(primary = "ns1.foo.gaz", contact =
                "hostmaster.foo", comment="123foo.gaz2")
        self.soa = s1
        d, _ = Domain.objects.get_or_create(name="bgaz")
        d.soa = s1
        d.save()
        self.dom = d
        self.soa.dirty = False
        self.dom.dirty = False

        s2, s1_c = SOA.objects.get_or_create(primary = "ns1.foo.gaz", contact =
                "hostmaster.foo", comment="123fooasdfsdf.gaz2")
        self.rsoa = s2
        rd, _ = ReverseDomain.objects.get_or_create(name="123")
        rd.soa = s2
        rd.save()
        self.rdom = rd
        self.rsoa.dirty = False
        self.rdom.dirty = False


    def test_dirty_a(self):
        self.soa.dirty = False
        self.dom.dirty = False
        a, _ = AddressRecord.objects.get_or_create(label="asfd",
                domain=self.dom, ip_str = "128.1.1.1", ip_type='4')
        a.save()
        self.assertTrue(self.dom.dirty)
        self.assertFalse(self.soa.dirty)

    def test_dirty_cname(self):
        self.soa.dirty = False
        self.dom.dirty = False
        c = CNAME(label="asfd", domain=self.dom, data="nerp")
        c.full_clean()
        c.save()
        self.assertTrue(self.dom.dirty)
        self.assertFalse(self.soa.dirty)

    def test_dirty_ptr(self):
        self.rsoa.dirty = False
        self.rdom.dirty = False
        c = PTR(name="asfd", ip_str="123.123.123.123", ip_type="4")
        c.full_clean()
        c.save()
        self.rdom = ReverseDomain.objects.get(pk=self.rdom.pk)
        self.assertTrue(self.rdom.dirty)
        self.assertFalse(self.rsoa.dirty)

    def test_dirty_mx(self):
        self.soa.dirty = False
        self.dom.dirty = False
        a, _ = MX.objects.get_or_create(label="asfd",
                domain=self.dom, server = "asdf", priority=123, ttl=44)
        a.save()
        self.assertTrue(self.dom.dirty)
        self.assertFalse(self.soa.dirty)

    def test_dirty_ns(self):
        self.soa.dirty = False
        self.dom.dirty = False
        a, _ = Nameserver.objects.get_or_create(domain=self.dom, server = "asdf")
        a.save()
        self.assertTrue(self.dom.dirty)
        self.assertFalse(self.soa.dirty)

    def test_dirty_rev_ns(self):
        self.rsoa.dirty = False
        self.rdom.dirty = False
        a, _ = ReverseNameserver.objects.get_or_create(domain=self.rdom,
                server = "asdf")
        a.save()
        self.assertTrue(self.rdom.dirty)
        self.assertFalse(self.rsoa.dirty)

    def test_dirty_rev_ns(self):
        self.rsoa.dirty = False
        self.rdom.dirty = False
        a, _ = ReverseNameserver.objects.get_or_create(reverse_domain=self.rdom,
                server = "asdf")
        a.save()
        self.assertTrue(self.rdom.dirty)
        self.assertFalse(self.rsoa.dirty)

    def test_dirty_soa(self):
        self.soa.dirty = False
        self.dom.dirty = False
        self.soa.refresh = 123
        self.soa.save()
        self.assertTrue(self.soa.dirty)

    def test_dirty_srv(self):
        self.soa.dirty = False
        self.dom.dirty = False
        a, _ = SRV.objects.get_or_create(label="_asf", port=22, domain=self.dom,
                target= "asdf", priority=123, weight=22)
        a.save()
        self.assertTrue(self.dom.dirty)
        self.assertFalse(self.soa.dirty)

    def test_dirty_txt(self):
        self.soa.dirty = False
        self.dom.dirty = False
        a, _ = TXT.objects.get_or_create(label="asf", txt_data="test",
                domain=self.dom)
        a.save()
        self.assertTrue(self.dom.dirty)
        self.assertFalse(self.soa.dirty)
