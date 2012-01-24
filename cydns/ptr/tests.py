"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import Reverse_Domain, add_reverse_domain
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.ptr.models import add_ipv4_ptr, add_ipv6_ptr, remove_ipv6_ptr, remove_ipv4_ptr
from cyder.cydns.ptr.models import update_ipv4_ptr, update_ipv6_ptr, PTRNotFoundError, PTR
from cyder.cydns.models import CyAddressValueError, InvalidRecordNameError

from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs
class PTRTests(TestCase):
    def setUp(self):
        self._128 = add_reverse_domain('128', ip_type='4')
        boot_strap_add_ipv6_reverse_domain("8.6.2.0")
        self.osu_block = "8620:105:F000:"

    def do_generic_add( self, ip, fqdn, ip_type, domain = None ):
        if ip_type = '4':
            ip_o = ipaddr.IPv4Address( ip )
            ip_upper, ip_lower = 0, ipaddr.IPv4Address(new_ip).__int__()
            add_ipv4_ptr( ip, fqdn )
        else:
            ip_o = ipaddr.IPv6Address( ip )
            ip_upper, ip_lower = ipv6_to_longs(new_ip)
            add_ipv6_ptr( ip, fqdn )

        ptr = PTR.objects.filter( name=fqdn, ip__ip_upper = ip_upper, ip__ip_lower = ip_lower, domain = domain )
        self.assertTrue(ptr)
        self.assertEqual( ptr[0].ip.__str__(), ip.__str__() )
        if domain:
            self.assertEqual( fqdn,ptr[0].name+"."+domain.name )
        else:
            self.assertEqual( fqdn,ptr[0].name )


    def test_add_ipv4_ptr(self):
        self.do_generic_add("128.193.1.1", "foo.bar.oregonstate.edu", '4')
        self.do_generic_add("128.194.1.1", "foo.bar.oregonsate.edu", '4')
        self.do_generic_add("128.196.1.1", "asdflkhasidfgwhqiefuhgiasdf.foo.bar.oregonstate.edu", '4')
        self.do_generic_add("128.193.3.1", "foo.bar.oregonstatesdfasdf.edu", '4')
        self.do_generic_add("128.193.10.2", "foo.bar.oregonstate.eddfsafsadfu", '4')
        self.do_generic_add("128.193.1.50", "foo.b213123123ar.oregonstate.edu", '4')
        self.do_generic_add("128.222.1.1", "foo.bar.oregondfastate.edu", '4')

    def test_add_ipv6_ptr(self):
        osu_block+"0:0:123:321::"
        self.do_generic_add(osu_block+":1", "foo.bar.oregonstate.edu", '4')
        self.do_generic_add(osu_block+":8", "foo.bar.oregonsate.edu", '4')
        self.do_generic_add(osu_block+":f", "asdflkhasidfgwhqiefuhgiasdf.foo.bar.oregonstate.edu", '4')
        self.do_generic_add(osu_block+":d", "foo.bar.oregonstatesdfasdf.edu", '4')
        self.do_generic_add(osu_block+":3", "foo.bar.oregonstate.eddfsafsadfu", '4')
        self.do_generic_add(osu_block+":2", "foo.b213123123ar.oregonstate.edu", '4')
        self.do_generic_add(osu_block+":5", "foo.bar.oregondfastate.edu", '4')


    def do_generic_invalid_add( self, ip, fqdn, ip_type, exception, domain = None ):
        e = None
        try:
            if ip_type = '4':
                add_ipv4_ptr( ip, fqdn )
            else:
                add_ipv6_ptr( ip, fqdn )
        except exception, e:
            pass
        self.assertEqual(exception, type(e)

    def test_add_invalid_name_ipv6_ptr(self):
        bad_name = "testyfoo.com"
        test_ip = self.osu_block+":1"
        bad_name = 123443214
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = "2134!@#$!@"
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = "asdflj..com"
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = True
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = False
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = "A"*257

    """
    Is this test redundant?
    """
    def test_add_invalid_name_ipv4_ptr(self):
        bad_name = "testyfoo.com"
        test_ip = "128.123.123.123"
        bad_name = 123443214
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = "2134!@#$!@"
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = "asdflj..com"
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = True
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = False
        self.do_generic_invalid_add( test_ip, bad_name, '6', InvalidRecordNameError )
        bad_name = "A"*257

    def test_add_invalid_ip_ipv6_ptr(self):
        test_name = "testyfoo.com"
        bad_ip = "123.123.123.123."
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = 1234
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = "123:!23:!23:"
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = "::"
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = None
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = True
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = False
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = lambda x: x
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )

    def test_add_invalid_ip_ipv4_ptr(self):
        test_name = "testyfoo.com"
        bad_ip = "123.123"
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = "asdfasdf"
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = 32141243
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = "128.123.123.123"
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = "...."
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = "1234."
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = None
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = False
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = True
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
