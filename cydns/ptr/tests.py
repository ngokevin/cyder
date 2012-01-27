"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import add_reverse_ipv4_domain, ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.domain.models import add_domain

from cyder.cydns.ptr.models import add_ipv4_ptr, add_ipv6_ptr, remove_ipv6_ptr, remove_ipv4_ptr
from cyder.cydns.ptr.models import update_ipv4_ptr, update_ipv6_ptr, PTR
from cyder.cydns.models import CyAddressValueError, InvalidRecordNameError

from cyder.cydns.ip.models import ipv6_to_longs, Ip
from cyder.cydns.cydns import trace
from cyder.cydns.models import RecordNotFoundError, RecordExistsError

import ipaddr
class PTRTests(TestCase):
    def setUp(self):
        self._128 = add_reverse_ipv4_domain('128')
        boot_strap_add_ipv6_reverse_domain("8.6.2.0")
        self.osu_block = "8620:105:F000:"
        self.o = add_domain("edu")
        self.o_e = add_domain("oregonstate.edu")
        self.b_o_e = add_domain("bar.oregonstate.edu")


    def do_generic_add( self, ip, fqdn, ip_type, domain = None ):
        if ip_type == '4':
            ip_o = ipaddr.IPv4Address( ip )
            ip_upper, ip_lower = 0, ipaddr.IPv4Address(ip).__int__()
            ret = add_ipv4_ptr( ip, fqdn )
        else:
            ip_o = ipaddr.IPv6Address( ip )
            ip_upper, ip_lower = ipv6_to_longs(ip)
            ret = add_ipv6_ptr( ip, fqdn )

        ptr = PTR.objects.filter( name=fqdn, ip__ip_upper = ip_upper, ip__ip_lower = ip_lower )
        ptr.__repr__()
        self.assertTrue(ptr)
        self.assertEqual( ptr[0].ip.__str__(), ip_o.__str__() )
        if domain:
            self.assertEqual( fqdn,ptr[0].name+"."+domain.name )
        else:
            self.assertEqual( fqdn,ptr[0].name )
        return ret


    def test_add_ipv4_ptr(self):
        ret = self.do_generic_add("128.193.1.1", "foo.bar.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.b_o_e )
        ret = self.do_generic_add("128.193.1.2", "foo.bar.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.b_o_e )
        ret = self.do_generic_add("128.193.1.1", "baasdfr.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.o_e )
        ret = self.do_generic_add("128.193.1.1", "fasdfasfdoo.bar.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.b_o_e )
        ret = self.do_generic_add("128.193.1.1", "lj21312bar.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.o_e )
        ret = self.do_generic_add("128.193.1.3", "baasdfr.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.o_e )
        ret = self.do_generic_add("128.193.1.7", "fasdfasfdoo.bar.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.b_o_e )
        ret = self.do_generic_add("128.193.16.1", "lj21312bar.oregonstate.edu", '4')
        self.assertEqual( ret.domain, self.o_e )
        ret = self.do_generic_add("128.193.16.1", "lj21312bar", '4')
        self.assertEqual( ret.domain, None )
        ret = self.do_generic_add("128.193.16.1", "ewr.rqewr.lj21312bar", '4')
        self.assertEqual( ret.domain, None )

    def test_add_ipv6_ptr(self):
        ret = self.do_generic_add(self.osu_block+":1", "foo.bar.oregonstate.edu", '6')
        self.assertEqual( ret.domain, self.b_o_e )
        ret = self.do_generic_add(self.osu_block+":8", "foo.bar.oregonstate.edu", '6')
        self.assertEqual( ret.domain, self.b_o_e )
        ret = self.do_generic_add(self.osu_block+":f", "asdflkhasidfgwhqiefuhgiasdf.foo.bar.oregonstate.edu", '6')
        self.assertEqual( ret.domain, self.b_o_e )
        ret = self.do_generic_add(self.osu_block+":d", "foo.bar.oregonstatesdfasdf.edu", '6')
        self.assertEqual( ret.domain, self.o )
        ret = self.do_generic_add(self.osu_block+":3", "foo.bar.oregonstate.eddfsafsadfu", '6')
        self.assertEqual( ret.domain, None )
        ret = self.do_generic_add(self.osu_block+":2", "foo.b213123123ar.oregonstate.edu", '6')
        self.assertEqual( ret.domain, self.o_e )
        ret = self.do_generic_add(self.osu_block+":5", "foo.bar.oregondfastate.com", '6')
        self.assertEqual( ret.domain, None)


    def do_generic_invalid_add( self, ip, fqdn, ip_type, exception, domain = None ):
        e = None
        try:
            if ip_type == '4':
                add_ipv4_ptr( ip, fqdn )
            else:
                add_ipv6_ptr( ip, fqdn )
        except exception, e:
            pass
        self.assertEqual(exception, type(e))

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
        bad_ip = ":::"
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = None
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = True
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = False
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = lambda x: x
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )

        bad_ip = "8::9:9:1"
        self.do_generic_invalid_add( bad_ip, test_name, '6', ReverseDomainNotFoundError )
        bad_ip = "11:9:9::1"
        self.do_generic_invalid_add( bad_ip, test_name, '6', ReverseDomainNotFoundError )

        bad_ip = "8.9.9.1"
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )
        bad_ip = "11.9.9.1"
        self.do_generic_invalid_add( bad_ip, test_name, '6', CyAddressValueError )

        bad_ip = self.osu_block+":233"
        self.do_generic_add(bad_ip, "foo.bar.oregonstate.edu", '6')
        self.do_generic_invalid_add( bad_ip, "foo.bar.oregonstate.edu", '6', RecordExistsError )
        self.do_generic_invalid_add( self.osu_block+":0:0:0233", "foo.bar.oregonstate.edu", '6', RecordExistsError )

        ret = self.do_generic_add(self.osu_block+":dd", "foo.bar.oregondfastate.com", '6')
        self.do_generic_invalid_add( self.osu_block+":dd", "foo.bar.oregondfastate.com", '6', RecordExistsError )

    def test_add_invalid_ip_ipv4_ptr(self):
        test_name = "testyfoo.com"
        bad_ip = "123.123"
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = "asdfasdf"
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = 32141243
        self.do_generic_invalid_add( bad_ip, test_name, '4', CyAddressValueError )
        bad_ip = "128.123.123.123.123"
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

        bad_ip = "8.9.9.1"
        self.do_generic_invalid_add( bad_ip, test_name, '4', ReverseDomainNotFoundError )
        bad_ip = "11.9.9.1"
        self.do_generic_invalid_add( bad_ip, test_name, '4', ReverseDomainNotFoundError )

        self.do_generic_add("128.193.1.1", "foo.bar.oregonstate.edu", '4')
        self.do_generic_invalid_add( "128.193.1.1", "foo.bar.oregonstate.edu", '4', RecordExistsError )

        ret = self.do_generic_add("128.128.1.1", "foo.bar.oregondfastate.com", '4')
        self.do_generic_invalid_add( "128.128.1.1", "foo.bar.oregondfastate.com", '4', RecordExistsError )

    def do_generic_remove( self, ip, fqdn, ip_type ):
        if ip_type == '4':
            ip_upper, ip_lower = 0, ipaddr.IPv4Address(ip).__int__()
            ptr = add_ipv4_ptr( ip, fqdn )
            remove_ipv4_ptr( ip, fqdn )
        else:
            ip_upper, ip_lower = ipv6_to_longs(ip)
            ptr = add_ipv6_ptr( ip, fqdn )
            remove_ipv6_ptr( ip, fqdn )

        ptr = PTR.objects.filter( name=fqdn, ip__ip_upper = ip_upper, ip__ip_lower = ip_lower, domain = ptr.domain )
        self.assertFalse(ptr)
        ip_search = Ip.objects.filter( ip_upper = ip_upper,ip_lower = ip_lower, ip_type = ip_type )
        self.assertFalse(ip_search)

    def test_remove_ipv4( self ):
        ip = "128.255.233.244"
        fqdn = "asdf34foo.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '4' )
        ip = "128.255.11.13"
        fqdn = "fo124kfasdfko.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '4' )
        ip = "128.255.9.1"
        fqdn = "or1fdsaflkegonstate.edu"
        self.do_generic_remove( ip, fqdn, '4' )
        ip = "128.255.1.7"
        fqdn = "12.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '4' )
        ip = "128.255.1.3"
        fqdn = "fcwoo.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '4' )
        ip = "128.255.1.2"
        fqdn = "asffad124jfasf-oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '4' )

    def test_remove_ipv6( self ):
        ip = self.osu_block+":1"
        fqdn = "asdf34foo.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '6' )
        ip = self.osu_block+":2"
        fqdn = "fo124kfasdfko.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '6' )
        ip = self.osu_block+":8"
        fqdn = "or1fdsaflkegonstate.edu"
        self.do_generic_remove( ip, fqdn, '6' )
        ip = self.osu_block+":8"
        fqdn = "12.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '6' )
        ip = self.osu_block+":20"
        fqdn = "fcwoo.bar.oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '6' )
        ip = self.osu_block+":ad"
        fqdn = "asffad124jfasf-oregonstate.edu"
        self.do_generic_remove( ip, fqdn, '6' )

    def do_generic_invalid_remove( self, ip, fqdn, ip_type, exception, domain = None ):
        e = None
        try:
            if ip_type == '4':
                remove_ipv4_ptr( ip, fqdn )
            else:
                remove_ipv6_ptr( ip, fqdn )
        except exception, e:
            pass
        self.assertEqual(exception, type(e))

    def test_invalid_remove_ipv4(self):
        add_ipv4_ptr( "128.193.1.1", "oregonstate.edu" )
        ip = "128.255.1.2"
        fqdn = "a23sffad124jfas11f-oregonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '4', RecordNotFoundError )
        fqdn = None
        self.do_generic_invalid_remove( ip, fqdn, '4', RecordNotFoundError )
        fqdn = "as$%#ffad124jfas11f-oregonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '4', InvalidRecordNameError )
        fqdn = True
        self.do_generic_invalid_remove( ip, fqdn, '4', InvalidRecordNameError )
        fqdn = "asff ad124jfasf-o11regonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '4', InvalidRecordNameError)
        fqdn = "asff..ad124jfasf-o11regonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '4', InvalidRecordNameError )
        fqdn = 1234
        self.do_generic_invalid_remove( ip, fqdn, '4', InvalidRecordNameError )

        fqdn = "oregonstate.edu"
        ip = "128.255.51..2"
        self.do_generic_invalid_remove( ip, fqdn, '4', RecordNotFoundError )
        ip = 1234124
        self.do_generic_invalid_remove( ip, fqdn, '4', RecordNotFoundError )
        ip = True
        self.do_generic_invalid_remove( ip, fqdn, '4', RecordNotFoundError )
        ip = None
        self.do_generic_invalid_remove( ip, fqdn, '4', RecordNotFoundError )

    def test_invalid_remove_ipv6(self):
        add_ipv6_ptr( self.osu_block+":1", "oregonstate.edu" )
        ip = self.osu_block+":1"
        fqdn = "a23sffad124jfas11f-oregonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '6', RecordNotFoundError )
        fqdn = "as$%#ffad124jfas11f-oregonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '6', InvalidRecordNameError )
        fqdn = "asff ad124jfasf-o11regonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '6', InvalidRecordNameError )
        fqdn = "asff..ad124jfasf-o11regonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '6', InvalidRecordNameError )
        fqdn = None
        self.do_generic_invalid_remove( ip, fqdn, '6', RecordNotFoundError )
        fqdn = True
        self.do_generic_invalid_remove( ip, fqdn, '6', InvalidRecordNameError )
        fqdn = 1234
        self.do_generic_invalid_remove( ip, fqdn, '6', InvalidRecordNameError )

        ip = "128.255.51..2"
        fqdn = "oregonstate.edu"
        self.do_generic_invalid_remove( ip, fqdn, '6', CyAddressValueError )
        ip = 1234124
        self.do_generic_invalid_remove( ip, fqdn, '6', CyAddressValueError )
        ip = True
        self.do_generic_invalid_remove( ip, fqdn, '6', CyAddressValueError )
        ip = None
        self.do_generic_invalid_remove( ip, fqdn, '6', CyAddressValueError )
        ip = self.osu_block+":dead"
        self.do_generic_invalid_remove( ip, fqdn, '6', RecordNotFoundError )

    def do_generic_update( self, ptr, new_fqdn, ip_type, domain = None ):
        if ip_type == '4':
            new_ptr = update_ipv4_ptr( ptr, new_fqdn )
        else:
            new_ptr = update_ipv4_ptr( ptr, new_fqdn )

        ptr = PTR.objects.filter( name=new_fqdn, ip__ip_upper = ptr.ip.ip_upper , ip__ip_lower = ptr.ip.ip_lower, domain = new_ptr.domain )
        self.assertTrue(ptr)
        if domain:
            self.assertEqual( new_fqdn,ptr[0].name+"."+domain.name )
        else:
            self.assertEqual( new_fqdn,ptr[0].name )

    def test_update_ipv4(self):
        ptr = add_ipv4_ptr( "128.193.1.1", "oregonstate.edu" )
        fqdn = "nothing.nothing.nothing"
        self.do_generic_update( ptr, fqdn, '4' )
        fqdn = "google.edu"
        self.do_generic_update( ptr, fqdn, '4' )
        fqdn = "asdfasfd.oregonstate.edu"
        self.do_generic_update( ptr, fqdn, '4' )
        fqdn = "asdfasf.foo.oregonstate.edu"
        self.do_generic_update( ptr, fqdn, '4' )
        fqdn = "edu"
        self.do_generic_update( ptr, fqdn, '4' )

    def test_update_ipv6(self):
        ptr = add_ipv6_ptr( self.osu_block+":1", "oregonstate.edu" )
        fqdn = "nothing.nothing.nothing"
        self.do_generic_update( ptr, fqdn, '6' )
        fqdn = "google.edu"
        self.do_generic_update( ptr, fqdn, '6' )
        fqdn = "asdfasfd.oregonstate.edu"
        self.do_generic_update( ptr, fqdn, '6' )
        fqdn = "asdfasf.foo.oregonstate.edu"
        self.do_generic_update( ptr, fqdn, '6' )
        fqdn = "edu"
        self.do_generic_update( ptr, fqdn, '6' )

    def do_generic_invalid_update( self, ptr, fqdn, ip_type, exception, domain = None ):
        e = None
        try:
            if ip_type == '4':
                update_ipv4_ptr( ptr, fqdn )
            else:
                update_ipv6_ptr( ptr, fqdn )
        except exception, e:
            pass
        self.assertEqual(exception, type(e))

    def test_invalid_update_ipv4( self ):
        ptr = add_ipv4_ptr( "128.193.1.1", "oregonstate.edu" )
        fqdn = "oregonstate.edu"
        self.do_generic_invalid_update( ptr, fqdn, '4', RecordExistsError )
        fqdn = "asfd..as"
        self.do_generic_invalid_update( ptr, fqdn, '4', InvalidRecordNameError )
        fqdn = 2134123412
        self.do_generic_invalid_update( ptr, fqdn, '4', InvalidRecordNameError )
        fqdn = "%.s#.com"
        self.do_generic_invalid_update( ptr, fqdn, '4', InvalidRecordNameError )
        fqdn = True
        self.do_generic_invalid_update( ptr, fqdn, '4', InvalidRecordNameError )
        fqdn = None
        self.do_generic_invalid_update( ptr, fqdn, '4', InvalidRecordNameError )

    def test_invalid_update_ipv6( self ):
        ptr = add_ipv6_ptr( self.osu_block+":aa", "oregonstate.edu" )
        fqdn = "oregonstate.edu"
        self.do_generic_invalid_update( ptr, fqdn, '6', RecordExistsError )
        fqdn = "asfd..as"
        self.do_generic_invalid_update( ptr, fqdn, '6', InvalidRecordNameError )
        fqdn = 2134123412
        self.do_generic_invalid_update( ptr, fqdn, '6', InvalidRecordNameError )
        fqdn = "%.s#.com"
        self.do_generic_invalid_update( ptr, fqdn, '6', InvalidRecordNameError )
        fqdn = True
        self.do_generic_invalid_update( ptr, fqdn, '6', InvalidRecordNameError )
        fqdn = None
        self.do_generic_invalid_update( ptr, fqdn, '6', InvalidRecordNameError )

    #TODO impliment this in cydns.domain.models
    """
    def test_reasign_domain( self ):
        _127 = add_reverse_ipv4_domain('127')
        boot_strap_add_ipv6_reverse_domain("9.6.2.0")
        osu_block = "9620:105:F000:"
        edu = add_domain("com")
        o_edu = add_domain("oregonstate.com")
        ptr0 = add_ipv4_ptr( "127.0.0.1", "foo.bar.oregonstate.com" )
        ptr1 = add_ipv6_ptr( osu_block+":1", "foo.bar.oregonstate.com" )
        self.assertTrue( ptr0.domain == o_edu )
        self.assertTrue( ptr1.domain == o_edu )

        b_o_edu = add_domain("bar.oregonstate.com")
        self.assertTrue( ptr0.domain == b_o_edu )
        self.assertTrue( ptr1.domain == b_o_edu )

        f_b_o_edu = add_domain("foo.bar.oregonstate.com")
        self.assertTrue( ptr0.domain == f_b_o_edu )
        self.assertTrue( ptr1.domain == f_b_o_edu )

        remove_domain("foo.bar.oregonstate.com")
        self.assertTrue( ptr0.domain == b_o_edu )
        self.assertTrue( ptr1.domain == b_o_edu )

        remove_domain("bar.oregonstate.com")
        self.assertTrue( ptr0.domain == o_edu )
        self.assertTrue( ptr1.domain == o_edu )

        remove_domain("oregonstate.com")
        self.assertTrue( ptr0.domain == edu )
        self.assertTrue( ptr1.domain == edu )

        remove_domain("com")
        self.assertTrue( ptr0.domain == None )
        self.assertTrue( ptr1.domain == None )

        edu = add_domain("com")
        self.assertTrue( ptr0.domain == edu )
        self.assertTrue( ptr1.domain == edu )

        o_edu = add_domain("oregonstate.com")
        self.assertTrue( ptr0.domain == o_edu )
        self.assertTrue( ptr1.domain == o_edu )
    """
