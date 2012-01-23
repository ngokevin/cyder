"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import Reverse_Domain, add_reverse_domain,ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain,remove_reverse_domain

from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs, Ip

from cyder.cydns.domain.models import Domain, add_domain, DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.domain.models import remove_domain_str, remove_domain, remove_domain, DomainNotFoundError

from cyder.cydns.models import InvalidRecordNameError
from cyder.cydns.address_record.models import RecordNotFoundError,add_AAAA_record,add_A_record
from cyder.cydns.address_record.models import remove_A_record,remove_AAAA_record, update_A_record, update_AAAA_record
from cyder.cydns.address_record.models import Address_Record,AddressValueError,RecordExistsError

import ipaddr
import pdb

class AddressRecordTests(TestCase):
    def setUp(self):
        try:
            add_domain('edu')
        except DomainExistsError, e:
            pass
        try:
            self.o_e = add_domain('oregonstate.edu')
        except DomainExistsError, e:
            self.o_e = Domain.objects.filter( name = 'oregonstate.edu' )[0]
            pass

        try:
            self.f_o_e = add_domain('foo.oregonstate.edu')
        except DomainExistsError, e:
            self.f_o_e = Domain.objects.filter( name = 'foo.oregonstate.edu' )[0]
            pass

        try:
            self.m_o_e = add_domain('max.oregonstate.edu')
        except DomainExistsError, e:
            self.m_o_e = Domain.objects.filter( name = 'max.oregonstate.edu' )[0]
            pass

        try:
            self.z_o_e = add_domain('zax.oregonstate.edu')
        except DomainExistsError, e:
            self.z_o_e = Domain.objects.filter( name = 'zax.oregonstate.edu' )[0]
            pass
        try:
            self.g_o_e = add_domain('george.oregonstate.edu')
        except DomainExistsError, e:
            self.g_o_e = Domain.objects.filter( name = 'george.oregonstate.edu' )[0]
            pass

        try:
            self._128 = add_reverse_domain('128', ip_type='4')
        except ReverseDomainExistsError, e:
            self._128 = Reverse_Domain.objects.filter( name = '128' )[0]
            pass

        try:
             self._128._193 = add_reverse_domain('128.193', ip_type='4')
        except ReverseDomainExistsError, e:
            self._128._193 = Reverse_Domain.objects.filter( name = '128.193' )[0]
            pass

    ######################
    ### Updating Tests ###
    ######################
    """
    Things that could go wrong.
    1) Update to an invalid ip.
    2) Update to an invalid name.
    """
    def _do_generic_update_test( self, record, new_name, new_ip, ip_type ):
        if new_ip:
            if ip_type == '4':
                ip_upper, ip_lower = 0, ipaddr.IPv4Address(new_ip).__int__()
            else:
                ip_upper, ip_lower = ipv6_to_longs(new_ip)
        else:
            ip_upper, ip_lower = record.ip.ip_upper, record.ip.ip_lower

        if new_name and new_ip:
            aret  = Address_Record.objects.filter( name = new_name, ip__ip_upper = ip_upper,\
                                             ip__ip_lower = ip_lower, ip__ip_type = ip_type).\
                                             select_related('ip')[0]
        elif new_name:
            # Just new_name
            aret  = Address_Record.objects.filter( name = new_name, ip__ip_upper = ip_upper,\
                                             ip__ip_lower = ip_lower, ip__ip_type = ip_type).\
                                             select_related('ip')[0]
        else:
            # Just new_ip
            aret  = Address_Record.objects.filter( name = record.name, ip__ip_upper = ip_upper,\
                                             ip__ip_lower = ip_lower, ip__ip_type = ip_type).\
                                             select_related('ip')[0]
        if new_name:
            self.assertEqual( aret.name, new_name )
        if new_ip:
            if ip_type == '4':
                self.assertEqual( aret.ip.__str__(), ipaddr.IPv4Address(new_ip).__str__() )
            else:
                self.assertEqual( aret.ip.__str__(), ipaddr.IPv6Address(new_ip).__str__() )

    def do_update_A_record( self, record, new_name, new_ip ):
        update_A_record( record , new_name, new_ip )
        self._do_generic_update_test( record, new_name, new_ip, '4' )

    def do_update_AAAA_record( self, record, new_name, new_ip ):
        update_AAAA_record( record , new_name, new_ip )
        self._do_generic_update_test( record, new_name, new_ip, '6' )


    def test_update_A_record(self):
        rec0 = add_A_record( '', self.m_o_e , "128.193.0.1")
        rec1 = add_A_record( 'foo', self.m_o_e , "128.193.0.1")
        rec2 = add_A_record( 'bar', self.m_o_e , "128.193.0.1")
        rec3 = add_A_record( 'bazisgoingtobelasdfhklashflashfllk-324-123n2319rjn2ddasfdasfd-sa', self.m_o_e , "128.193.0.1")
        rec4 = add_A_record( 'rees', self.m_o_e , "128.193.0.1")
        self.do_update_A_record( rec0, "whooooop1", "128.193.23.1")
        self.do_update_A_record( rec1, "whoooasfdasdflasdfjoop3", "128.193.23.2")
        self.do_update_A_record( rec2, "whsdflhjsafdohaosdfhsadooooop1", "128.193.23.4")
        self.do_update_A_record( rec3, "wasdflsadhfaoshfuoiwehfjsdkfavbhooooop1", "128.193.23.3")
        self.do_update_A_record( rec0, "liaslfdjsa8df09823hsdljf-whooooop1", "128.193.25.17")
        self.do_update_A_record( rec1, "w", "128.193.29.83")
        self.do_update_A_record( rec0, None, "128.193.23.1")
        self.do_update_A_record( rec1, "whoooasfdasdflasdfjoop3", None)

    def test_update_AAAA_record(self):
        osu_block = "8620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("8.6.2.0")
        rec0 = add_AAAA_record( '', self.z_o_e , osu_block+":1")
        rec1 = add_AAAA_record( 'foo', self.z_o_e , osu_block+":1")
        rec2 = add_AAAA_record( 'bar', self.z_o_e , osu_block+":1")
        self.do_update_AAAA_record( rec0, "whoooooasfjsp1", osu_block+"0:0:123:321::")
        self.do_update_AAAA_record( rec1, "wasfasfsafdhooooop1", osu_block+"0:0:123:321::")
        self.do_update_AAAA_record( rec2, "whoooooasfdisafsap1", osu_block+"0:24:123:322:1")
        self.do_update_AAAA_record( rec0, "whooooop1", osu_block+"0:aaa::1")
        self.do_update_AAAA_record( rec0, "wasflasksdfhooooop1", osu_block+"0:dead::")
        self.do_update_AAAA_record( rec1, "whooooosf13fp1", osu_block+"0:0::")
        self.do_update_AAAA_record( rec1, "whooooodfijasf1", osu_block+"0:1:23::")
        self.do_update_AAAA_record( rec2, "lliasdflsafwhooooop1", osu_block+":")
        self.do_update_AAAA_record( rec1, "whooooopsjafasf1", osu_block+"0::")
        self.do_update_AAAA_record( rec2, None, osu_block+":")
        self.do_update_AAAA_record( rec1, "whooooopsjafasf1", None)
        self.do_update_AAAA_record( rec0, None, osu_block+"0:0:123:321::")
        self.do_update_AAAA_record( rec1, None, osu_block+"0:0:123:321::")

    def test_update_invalid_ip_A_record(self):
        osu_block = "7620:105:F000:"
        rec0 = add_A_record( 'z', self.g_o_e , "128.193.254.1")
        # BAD Names
        try:
            self.do_update_A_record( rec0, " sdfsa ", None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, -1, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, 34871, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, None, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        # BAD IPs
        try:
            self.do_update_A_record( rec0, None, 71134)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, None, "19.193.23.1.2")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, None, 12314123)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, "narf", 1214123)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, "%asdfsaf", "1928.193.23.1")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, None, "1928.193.23.1")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None

        try:
            self.do_update_A_record( None, "asdfa", osu_block+":1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None
        try:
            self.do_update_A_record( rec0, "asdfa", "88.67.67.67")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))
        e = None

    def test_update_invalid_ip_AAAA_record(self):
        osu_block = "7620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("7.6.2.0")
        rec0 = add_AAAA_record( '', self.g_o_e , osu_block+":1")
        try:
            self.do_update_AAAA_record( rec0, None, 71134)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, None, osu_block+":::")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, "%asdfsaf", osu_block)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, "sdfsa", 1239812472934623847)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, None, "128.193.1.1")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, -1, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, None, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, "%asdfsaf", osu_block+":1")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( rec0, " sdfsa ", None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            self.do_update_AAAA_record( None, "asdfa", osu_block+":1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None

        try:
            self.do_update_AAAA_record( rec0, "asdfa", "6435:234:"+":1")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))
        e = None


    ######################
    ### Removing Tests ###
    ######################
    def do_remove_A_record(self, aname, domain, ip ):
        ip_int= ipaddr.IPv4Address(ip).__int__()
        add_A_record( aname, domain , ip )
        aret  = Address_Record.objects.filter( name = aname )
        ipret = Ip.objects.filter( ip_lower = ip_int, ip_type='4' )
        self.assertTrue(aret)
        self.assertTrue(ipret)

        remove_A_record(aname, domain, ip)

        aret  = Address_Record.objects.filter( name = aname, domain = domain, ip = ipret )
        ipret = Ip.objects.filter( ip_lower = ip_int, ip_type='4' )
        self.assertFalse(aret)
        self.assertFalse(ipret)

    def do_remove_AAAA_record(self, aname, domain, ip ):
        ip_upper, ip_lower= ipv6_to_longs(ip)
        add_AAAA_record( aname, domain , ip )
        aret  = Address_Record.objects.filter( name = aname )
        ipret = Ip.objects.filter( ip_upper = ip_upper, ip_lower = ip_lower, ip_type='6' )
        self.assertTrue(aret)
        self.assertTrue(ipret)

        remove_AAAA_record( aname, domain, ip )

        aret  = Address_Record.objects.filter( name = aname, domain = domain, ip = ipret )
        ipret = Ip.objects.filter( ip_upper = ip_upper, ip_lower = ip_lower, ip_type='6' )
        self.assertFalse(aret)
        self.assertFalse(ipret)


    def test_remove_A_address_records(self):
        self.do_remove_A_record("", self.o_e, "128.193.0.1" )
        self.do_remove_A_record("far", self.o_e, "128.193.0.2" )
        self.do_remove_A_record("fetched", self.o_e, "128.193.1.1" )
        self.do_remove_A_record("drum", self.o_e, "128.193.2.1" )
        self.do_remove_A_record("and", self.o_e, "128.193.0.3" )
        self.do_remove_A_record("bass", self.o_e, "128.193.2.2" )
        self.do_remove_A_record("dude", self.o_e, "128.193.5.1" )
        self.do_remove_A_record("man", self.o_e, "128.193.1.4" )
        self.do_remove_A_record("right", self.o_e, "128.193.2.6" )
        self.do_remove_A_record("", self.f_o_e, "128.193.0.1" )
        self.do_remove_A_record("far", self.f_o_e, "128.193.0.2" )
        self.do_remove_A_record("fetched", self.f_o_e, "128.193.1.1" )
        self.do_remove_A_record("drum", self.f_o_e, "128.193.2.1" )
        self.do_remove_A_record("and", self.f_o_e, "128.193.0.3" )
        self.do_remove_A_record("bass", self.f_o_e, "128.193.2.2" )
        self.do_remove_A_record("dude", self.f_o_e, "128.193.5.1" )
        self.do_remove_A_record("man", self.f_o_e, "128.193.1.4" )
        self.do_remove_A_record("right", self.f_o_e, "128.193.2.6" )

    def test_remove_AAAA_address_records(self):
        osu_block = "4620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("4.6.2.0")
        self.do_remove_AAAA_record("", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record("please", self.o_e, osu_block+":2" )
        self.do_remove_AAAA_record("visit", self.o_e, osu_block+":4" )
        self.do_remove_AAAA_record("from", self.o_e, osu_block+":2" )
        self.do_remove_AAAA_record("either", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record("webpages", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record("read", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record("", self.f_o_e, osu_block+":1" )
        self.do_remove_AAAA_record("please", self.f_o_e, osu_block+":2" )
        self.do_remove_AAAA_record("visit", self.f_o_e, osu_block+":4" )
        self.do_remove_AAAA_record("from", self.f_o_e, osu_block+":2" )
        self.do_remove_AAAA_record("either", self.f_o_e, osu_block+":1" )
        self.do_remove_AAAA_record("webpages", self.f_o_e, osu_block+":1" )
        self.do_remove_AAAA_record("read", self.f_o_e, osu_block+":1" )

    def test_remove_nonexistant_A_address_records(self):
        try:
            remove_A_record("pretty_sure_it_doesn_exist0", self.f_o_e, "128.193.0.1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None

        try:
            remove_A_record("", self.f_o_e,"123.123.123.123")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None

        try:
            remove_A_record("pretty_sure_it_doesn_exist0", self.o_e, "128.193.1.1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None

        try:
            remove_A_record("", self.f_o_e, "")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None

        try:
            remove_A_record("", self.f_o_e, 124231)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None

    def test_remove_nonexistant_AAAA_address_records(self):
        osu_block = "5620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("5.6.2.0")
        try:
            remove_AAAA_record("pretty_sure_it_doesn_exist0", self.f_o_e, osu_block+":1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None
        #++++++++++++++++
        try:
            remove_AAAA_record("", self.f_o_e, osu_block+":1")
        except RecordNotFoundError, e:
            pass
        try:
            remove_AAAA_record("", self.f_o_e, osu_block+":1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None
        #++++++++++++++++
        try:
            remove_AAAA_record("pretty_sure_it_doesn_exist0", self.o_e, osu_block+":1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None
        #++++++++++++++++
        try:
            remove_AAAA_record("", self.f_o_e, osu_block+":1")
        except RecordNotFoundError, e:
            pass
        try:
            remove_AAAA_record("", self.f_o_e, osu_block+":1")
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        e = None

    ####################
    ### Adding Tests ###
    ####################

    def test_add_A_address_records(self):
        rec = add_A_record( '', self.o_e , "128.193.0.1")
        self.assertEqual( rec.__str__(), "oregonstate.edu A 128.193.0.1" )
        add_A_record( '', self.f_o_e , "128.193.0.6")
        rec = add_A_record( 'ba3z', self.o_e , "128.193.0.3")
        self.assertEqual( rec.__str__(), "ba3z.oregonstate.edu A 128.193.0.3" )
        add_A_record( 'ba3z', self.f_o_e , "128.193.0.8")
        add_A_record( 'foob1ar', self.f_o_e , "128.193.0.10")
        add_A_record( 'foob1ar', self.o_e , "128.193.0.5")
        add_A_record( 'foo2', self.f_o_e , "128.193.0.7")
        add_A_record( 'foo2', self.o_e , "128.193.0.2")
        add_A_record( 'ba-r', self.f_o_e , "128.193.0.9")
        add_A_record( 'ba-r', self.o_e , "128.193.0.4")
        rec = add_A_record( 'somthingreallylongthatmightactuallybeaddedinttherealworl-r', self.o_e , "128.193.0.4")
        self.assertEqual( rec.__str__(), "somthingreallylongthatmightactuallybeaddedinttherealworl-r.oregonstate.edu A 128.193.0.4" )

    def test_add_AAAA_address_records(self):
        osu_block = "2620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("2.6.2.0")
        rec = add_AAAA_record( '', self.f_o_e , osu_block+":4")
        self.assertEqual( rec.__str__(), "foo.oregonstate.edu AAAA 2620:105:f000::4" )
        rec = add_AAAA_record( '', self.o_e , osu_block+":1")
        rec = add_AAAA_record( '6ba-r', self.o_e , osu_block+":6")
        rec = add_AAAA_record( '6ba-r', self.f_o_e , osu_block+":7")
        self.assertEqual( rec.__str__(), "6ba-r.foo.oregonstate.edu AAAA 2620:105:f000::7" )
        add_AAAA_record( '6foo', self.f_o_e , osu_block+":5")
        add_AAAA_record( '6foo', self.o_e , osu_block+":3")
        add_AAAA_record( '6ba3z', self.o_e , osu_block+":4")
        add_AAAA_record( '6ba3z', self.f_o_e , osu_block+":6")
        add_AAAA_record( '6foob1ar', self.o_e , osu_block+":5")
        add_AAAA_record( '6foob1ar', self.f_o_e , osu_block+":8")
        add_AAAA_record( '23412341253254243', self.f_o_e , osu_block+":8")

    def test_bad_A_ip(self):
        #IPv4 Tests
        osu_block = "2620:105:F000:"
        try:
            add_A_record( 'asdf0', self.o_e , osu_block+":1")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None

        try:
            add_A_record( 'asdf1', self.o_e , 123142314)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None

        try:
            add_A_record( 'asdf1', self.o_e , "128.193.0.1.22")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        try:
            add_A_record( 'asdf2', self.o_e , "128.193.8")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            add_A_record( 'asdf3', self.o_e , "99.193.8.1")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))
        e = None

    def test_bad_AAAA_ip(self):
        # IPv6 Tests
        osu_block = "2620:105:F000:"
        try:
            add_AAAA_record( 'asdf5', self.o_e , "128.193.8.1")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None
        try:
            add_AAAA_record( 'asdf4', self.o_e , osu_block+":::")
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None

        try:
            add_AAAA_record( 'asdf4', self.o_e , 123213487823762347612346)
        except AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        e = None

        try:
            add_AAAA_record( 'asdf6', self.o_e , "9::1")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))
        e = None
        try:
            add_AAAA_record( 'asdf6', self.o_e , "9213:123:213:12::1")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))
        e = None

    def test_add_A_records_exist(self):
        try:
            add_A_record( '', self.f_o_e,"128.193.0.2" )
        except RecordExistsError, e:
            pass
        try:
            add_A_record( '', self.f_o_e ,"128.193.0.2" )
        except RecordExistsError, e:
            pass
        add_A_record( 'new', self.f_o_e,"128.193.0.2" )
        try:
            add_A_record( 'new', self.f_o_e ,"128.193.0.2" )
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))
        e = None
        add_A_record( 'nope', self.o_e ,"128.193.0.2" )
        try:
            add_A_record( 'nope', self.o_e ,"128.193.0.2" )
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))
        e = None

    def test_add_AAAA_records_exist(self):
        osu_block = "9620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("9.6.2.0")
        add_AAAA_record( 'new', self.f_o_e,osu_block+":2")
        try:
            add_AAAA_record( 'new', self.f_o_e ,osu_block+":2")
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))
        e = None
        add_AAAA_record( 'nope', self.o_e ,osu_block+":4")
        try:
            add_AAAA_record( 'nope', self.o_e ,osu_block+":4")
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))
        e = None

    def test_add_A_invalid_address_records(self):
        try:
            add_A_record( 'foo.nas', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_A_record( 'foo.bar.nas', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_A_record( 'foo.baz.bar.nas', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_A_record( 'n as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_A_record( 'n as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            add_A_record( 'n%as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            add_A_record( 'n+as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

    def test_add_AAAA_invalid_address_records(self):
        osu_block = "3620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("3.6.2.0")
        try:
            add_AAAA_record( 'foo.nas', self.o_e , osu_block+":1")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_AAAA_record( 'foo.bar.nas', self.o_e ,osu_block+":2")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_AAAA_record( 'foo.baz.bar.nas', self.o_e ,osu_block+":3")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_AAAA_record( 'n as', self.o_e ,osu_block+":4")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None

        try:
            add_AAAA_record( 'n!+/*&%$#@as', self.o_e ,osu_block+":5")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            add_AAAA_record( 'n%as', self.o_e ,osu_block+":6")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
        try:
            add_AAAA_record( 'n+as', self.o_e ,osu_block+":7")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        e = None
