"""
OSU IPv6 allocation:
    2620:105:F000::/40
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import Reverse_Domain, add_reverse_ipv4_domain
from cyder.cydns.reverse_domain.models import add_reverse_ipv6_domain, ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs

from cyder.cydns.domain.models import Domain, add_domain, DomainExistsError, MasterDomainNotFoundError, remove_domain, DomainNotFoundError
from cyder.cydns.domain.models import remove_domain_str, remove_domain

import ipaddr
import pdb

class SimpleTest(TestCase):
    def setUp(self):
        self.com_domain = add_domain('com', None )

    def test_remove_domain(self):
        add_domain('foo.com', self.com_domain )
        remove_domain_str('foo.com')
        foo = add_domain('foo.com', self.com_domain )
        remove_domain(foo)

    def test_remove_nonexistent_domain(self):
        try:
            remove_domain_str('fooasdfcom')
        except DomainNotFoundError, e:
            pass
        self.assertEqual( DomainNotFoundError, type(e))

    def test__name_to_master_domain(self):
        try:
            add_domain('foo.cn', None )
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))

        cn = add_domain('cn', master_domain=None )
        add_domain('foo.cn', master_domain=cn )
        try:
            add_domain('foo.cn', master_domain=cn )
        except DomainExistsError, e:
            pass
        self.assertEqual( DomainExistsError, type(e))


    def test_create_domain(self):
        edu = add_domain('edu', master_domain=None)
        add_domain('oregonstate.edu', master_domain=edu )
        try:
            add_domain('foo.bar.oregonstate.edu', master_domain=edu )
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))

    def test_boot_strap_add_ipv6_domain(self):
        osu_block = "2621:105:F000"
        test_dname = osu_block+":dead:beef::"
        boot_strap_add_ipv6_reverse_domain( test_dname )
        try:
            add_reverse_ipv6_domain('2621:105:f000::')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        try:
            add_reverse_ipv6_domain('2621::')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        try:
            add_reverse_ipv6_domain('2621:105:F000:dead::')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        try:
            add_reverse_ipv6_domain('2621:105:F000:dead:beef::')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        try:
            add_reverse_ipv6_domain(test_dname)
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        # These should pass
        #boot_strap_add_ipv6_reverse_domain('2622:1053:f000:1234:1234:1234:1234:1234')
        #boot_strap_add_ipv6_reverse_domain('2623:1053:f000:1234:1234:1234:1234::')
        # ^ That one doesn't pass due to this issue https://gist.github.com/1576412
        # Those are pretty unrealistic since they prodtrude into the host part of the address.
        boot_strap_add_ipv6_reverse_domain('2623:1053:f000:1234:1234:1234::')
        boot_strap_add_ipv6_reverse_domain('2624::')
        boot_strap_add_ipv6_reverse_domain('2625:1::')

    # Reverse Domain test functions
    def test_remove_reverse_domain(self):
        add_reverse_ipv4_domain('128')
        rd = add_reverse_ipv4_domain('128.193')
        ip1 = add_str_ipv4('128.193.8.1')
        self.assertEqual( ip1.reverse_domain, rd )
        ip2 = add_str_ipv4('128.193.8.2')
        self.assertEqual( ip2.reverse_domain, rd )
        ip3 = add_str_ipv4('128.193.8.3')
        self.assertEqual( ip3.reverse_domain, rd )
        ip4 = add_str_ipv4('128.193.8.4')
        self.assertEqual( ip4.reverse_domain, rd )
        rd = add_reverse_ipv4_domain('128.193.8')
        self.assertEqual( ip1.reverse_domain, rd )
        self.assertEqual( ip2.reverse_domain, rd )
        self.assertEqual( ip3.reverse_domain, rd )
        self.assertEqual( ip4.reverse_domain, rd )

        osu_block = "2620:105:F000"
        rd = add_reverse_ipv4_domain(osu_block+":8::1")
        ip1 = add_str_ipv4(osu_block+":8::1")
        self.assertEqual( ip1.reverse_domain, rd )
        ip2 = add_str_ipv4(osu_block+":8::2")
        self.assertEqual( ip2.reverse_domain, rd )
        ip3 = add_str_ipv4(osu_block+":8::3")
        self.assertEqual( ip3.reverse_domain, rd )
        ip4 = add_str_ipv4(osu_block+":8::4")
        self.assertEqual( ip4.reverse_domain, rd )
        rd = add_reverse_ipv4_domain(osu_block+":8::")
        self.assertEqual( ip1.reverse_domain, rd )
        self.assertEqual( ip2.reverse_domain, rd )
        self.assertEqual( ip3.reverse_domain, rd )
        self.assertEqual( ip4.reverse_domain, rd )

    def test_add_reverse_domains(self):
        try:
            add_reverse_ipv4_domain('192.168')
        except ReverseMasterDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseMasterDomainNotFoundError, e)
        add_reverse_ipv4_domain('192')
        add_reverse_ipv4_domain('192.168')
        try:
            add_reverse_ipv4_domain('192.168')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual(ReverseDomainExistsError, e)

    def test_add_reverse_domainless_ips(self):
        try:
            add_str_ipv4('8.8.8.8')
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual( ReverseDomainNotFoundError, type(e))

        try:
            add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual( ReverseDomainNotFoundError, type(e))

        add_reverse_ipv6_domain('2001:0db8:85a3:0000:0000::')
        try:
            add_reverse_ipv6_domain('2001:0db8:85a3::')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))

        add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')

    def test_ipv6_to_longs(self):
        ip = ipaddr.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        ret = ipv6_to_longs(ip.__str__())
        self.assertEqual( ret, (2306139570357600256,151930230802227))
