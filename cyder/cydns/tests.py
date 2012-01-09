"""
OSU IPv6 allocation:
    2620:105:F000::/40
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import Reverse_Domain, add_reverse_ipv4_domain
from cyder.cydns.reverse_domain.models import add_reverse_ipv6_domain, ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain,remove_reverse_ipv4_domain

from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs, Ip

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


    # Reverse Domain test functions

    def test_remove_reverse_ipv4_domain(self):
        add_reverse_ipv4_domain('127')
        rd1 = add_reverse_ipv4_domain('127.193')
        rd2 = add_reverse_ipv4_domain('127.193.8')
        #pdb.set_trace()
        ip1 = add_str_ipv4('127.193.8.1')
        self.assertEqual( ip1.reverse_domain, rd2 )
        ip2 = add_str_ipv4('127.193.8.2')
        self.assertEqual( ip2.reverse_domain, rd2 )
        ip3 = add_str_ipv4('127.193.8.3')
        self.assertEqual( ip3.reverse_domain, rd2 )
        ip4 = add_str_ipv4('127.193.8.4')
        self.assertEqual( ip4.reverse_domain, rd2 )
        remove_reverse_ipv4_domain('127.193.8')
        ip1 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('127.193.8.1').__int__(), ip_type = '4')[0]
        self.assertEqual( ip1.reverse_domain, rd1 )
        ip2 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('127.193.8.2').__int__(), ip_type = '4')[0]
        self.assertEqual( ip2.reverse_domain, rd1 )
        ip3 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('127.193.8.2').__int__(), ip_type = '4')[0]
        self.assertEqual( ip3.reverse_domain, rd1 )
        ip4 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('127.193.8.3').__int__(), ip_type = '4')[0]
        self.assertEqual( ip4.reverse_domain, rd1 )


    def test_master_reverse_ipv4_domains(self):
        rd1 =add_reverse_ipv4_domain('128')
        rd2 = add_reverse_ipv4_domain('128.193')
        rd3 = add_reverse_ipv4_domain('128.193.8')
        self.assertEqual( rd3.master_reverse_domain, rd2 )
        self.assertEqual( rd2.master_reverse_domain, rd1 )
        self.assertEqual( rd1.master_reverse_domain, None )



    def test_add_reverse_ipv4_domains(self):
        try:
            add_reverse_ipv4_domain('192.168')
        except MasterReverseDomainNotFoundError, e:
            pass
        self.assertEqual( MasterReverseDomainNotFoundError, type(e))
        add_reverse_ipv4_domain('192')
        add_reverse_ipv4_domain('192.168')
        try:
            add_reverse_ipv4_domain('192.168')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual(ReverseDomainExistsError, type(e))

        rd = add_reverse_ipv4_domain('128')
        rd0 = add_reverse_ipv4_domain('128.193')
        ip1 = add_str_ipv4('128.193.8.1')
        self.assertEqual( ip1.reverse_domain, rd0 )
        ip2 = add_str_ipv4('128.193.8.2')
        self.assertEqual( ip2.reverse_domain, rd0 )
        ip3 = add_str_ipv4('128.193.8.3')
        self.assertEqual( ip3.reverse_domain, rd0 )
        ip4 = add_str_ipv4('128.193.8.4')
        self.assertEqual( ip4.reverse_domain, rd0 )
        rd1 = add_reverse_ipv4_domain('128.193.8')
        ip1 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.1').__int__(), ip_type = '4')[0]
        self.assertEqual( ip1.reverse_domain, rd1 )
        ip2 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.2').__int__(), ip_type = '4')[0]
        self.assertEqual( ip2.reverse_domain, rd1 )
        ip3 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.3').__int__(), ip_type = '4')[0]
        self.assertEqual( ip3.reverse_domain, rd1 )
        ip4 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.4').__int__(), ip_type = '4')[0]
        self.assertEqual( ip4.reverse_domain, rd1 )
        remove_reverse_ipv4_domain('128.193.8')
        ip1 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.1').__int__(), ip_type = '4')[0]
        self.assertEqual( ip1.reverse_domain, rd0 )
        ip2 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.2').__int__(), ip_type = '4')[0]
        self.assertEqual( ip2.reverse_domain, rd0 )
        ip3 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.2').__int__(), ip_type = '4')[0]
        self.assertEqual( ip3.reverse_domain, rd0 )
        ip4 = Ip.objects.filter(ip_lower = ipaddr.IPv4Address('128.193.8.3').__int__(), ip_type = '4')[0]
        self.assertEqual( ip4.reverse_domain, rd0 )

    """
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
    """

    """
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
        boot_strap_add_ipv6_reverse_domain('2001:0db8:85a3::')
        try:
            add_reverse_ipv6_domain('2001:0db8:85a3::')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))

        add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')
    """

    def test_ipv6_to_longs(self):
        ip = ipaddr.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        ret = ipv6_to_longs(ip.__str__())
        self.assertEqual( ret, (2306139570357600256,151930230802227))
    """
    def test_remove_reverse_ipv6_domain(self):
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
    """
    def test_add_reverse_ipv6_domains(self):
        osu_block = "2620:105:F000"
        rd0 = boot_strap_add_ipv6_reverse_domain("2.6.2.0.0.1.0.5.f.0.0.0")
        ip1 = add_str_ipv6(osu_block+":8000::1")
        self.assertEqual( ip1.reverse_domain, rd0 )
        ip2 = add_str_ipv6(osu_block+":8000::2")
        self.assertEqual( ip2.reverse_domain, rd0 )
        ip3 = add_str_ipv6(osu_block+":8000::3")
        self.assertEqual( ip3.reverse_domain, rd0 )
        ip4 = add_str_ipv6(osu_block+":8000::4")
        rd1 = add_reverse_ipv4_domain("2.6.2.0.0.1.0.5.f.0.0.0.8",ip_type='6')
        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::1")
        ip1 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip1.reverse_domain, rd1 )
        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::2")
        ip2 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip2.reverse_domain, rd1 )
        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::3")
        ip3 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip3.reverse_domain, rd1 )
        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::4")
        ip4 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip4.reverse_domain, rd1 )
    """
    def test_master_reverse_ipv6_domains(self):
        rd1 =add_reverse_ipv4_domain('1283::')
        rd2 = add_reverse_ipv4_domain('1283:0::')
        rd3 = add_reverse_ipv4_domain('1283:0:4345::')
        self.assertEqual( rd3.master_reverse_domain, rd2 )
        self.assertEqual( rd2.master_reverse_domain, rd1 )
        self.assertEqual( rd1.master_reverse_domain, None )
    """
