"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import ipaddr
from cyder.cydns.ip.models import ipv6_to_longs, Ip
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain, ReverseDomain, ReverseDomainExistsError
from cyder.cydns.models import CyAddressValueError
import pdb

class SimpleTest(TestCase):
    def test_ipv4_str(self):
        rd = ReverseDomain(name='192', ip_type='4')
        rd.save()
        ip_str = '192.168.1.1'
        ip = ipaddr.IPv4Address(ip_str)
        Ip( ip_str = ip_str, ip_type='4' ).save()
        new_ip = Ip.objects.filter( ip_upper = 0, ip_lower = ip.__int__(), reverse_domain = rd, ip_type = '4' )
        self.assertTrue(new_ip)

        rd = ReverseDomain(name='128', ip_type='4')
        rd.save()
        ip_str = '128.168.1.1'
        ip = ipaddr.IPv4Address(ip_str)
        Ip( ip_str = ip_str, ip_type = '4' ).save()
        new_ip = Ip.objects.filter( ip_upper = 0, ip_lower = ip.__int__(), reverse_domain = rd, ip_type = '4')
        self.assertTrue(new_ip)


    def test_ipv6_str(self):
        rd = boot_strap_add_ipv6_reverse_domain('1.2.3.4')

        ip_str = '1234:1234:1243:1243:1243::'
        Ip( ip_str = ip_str, ip_type='6' ).save()

        ip_upper, ip_lower = ipv6_to_longs(ip_str)
        new_ip = Ip.objects.filter( ip_upper = ip_upper, ip_lower = ip_lower, reverse_domain = rd, ip_type = '6')
        self.assertTrue(new_ip)

        ip_str = '1234:432:3:0:3414:22::'
        Ip( ip_str = ip_str, ip_type='6' ).save()

        ip_upper, ip_lower = ipv6_to_longs(ip_str)
        new_ip = Ip.objects.filter( ip_upper = ip_upper, ip_lower = ip_lower, reverse_domain = rd, ip_type = '6')
        self.assertTrue(new_ip)

    def test_large_ipv6(self):
        try:
            rd = boot_strap_add_ipv6_reverse_domain('f')
            rd.save()
        except ReverseDomainExistsError, e:
            pass
        ip_str = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        ip = ipaddr.IPv6Address(ip_str)
        ip_upper, ip_lower = ipv6_to_longs(ip_str)
        self.assertEqual( ip.__int__(), (2**64)*ip_upper + ip_lower)
        new_ip = Ip( ip_str= ip_str, ip_upper = ip_upper, ip_lower = ip_lower, reverse_domain = rd, ip_type = '6')
        new_ip.clean()
        self.assertEqual(ip_str, new_ip.__str__())
        self.assertEqual(ip.__int__(), new_ip.__int__())

    def bad_ipv6(self):
        self.assertRaises(CyAddressValueError, ipv6_to_longs, {'addr':"1::::"})


    def test_int_ip(self):
        rd = ReverseDomain(name='129', ip_type='4')
        rd.save()
        ip = Ip( ip_str = "129.193.1.1", ip_type='4' )
        ip.clean()
        ip.__int__()
        ip.__repr__()
        rd = boot_strap_add_ipv6_reverse_domain('e')
        ip_str = 'efff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        ip = Ip(ip_str = ip_str, ip_type = '6')
        ip.clean()
        ip.__int__()
        ip.__repr__()

    def test_creation(self):
        rd = ReverseDomain(name='130', ip_type='4')
        rd.save()
        try:
            ip = Ip( ip_str = "130.193.1.2" ) # Forget the ip_type
            ip.clean()

        except CyAddressValueError, e:
            pass
        self.assertEqual( CyAddressValueError, type(e))

        ip = Ip( ip_str = "130.193.1.2", ip_type='4' )
        self.assertFalse( ip.ip_upper and ip.ip_lower and ip.reverse_domain )
        ip.clean()
        self.assertTrue( ip.ip_upper==0 and ip.ip_lower and ip.reverse_domain )
