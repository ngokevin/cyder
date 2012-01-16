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

from cyder.cydns.address_record.models import remove_domain_str, remove_domain, remove_domain, RecordExistsError
from cyder.cydns.address_record.models import InvalidRecordNameError,RecordNotFoundError,add_AAAA_record,add_A_record
from cyder.cydns.address_record.models import remove_A_record,remove_AAAA_record, update_A_record, update_AAAA_record
from cyder.cydns.address_record.models import Address_Record,AddressValueError

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
            pass
        try:
            self.o_e = Domain.objects.filter( name = 'oregonstate.edu' )
        except DomainExistsError, e:
            pass
        try:
            self.f_o_e = Domain.objects.filter( name = 'foo.oregonstate.edu' )
        except DomainExistsError, e:
            pass
        try:
            self.m_o_e = Domain.objects.filter( name = 'max.oregonstate.edu' )
        except DomainExistsError, e:
            pass
        try:
            self.z_o_e = Domain.objects.filter( name = 'zax.oregonstate.edu' )
        except DomainExistsError, e:
            pass
        try:
            self.g_o_e = Domain.objects.filter( name = 'george.oregonstate.edu' )
        except DomainExistsError, e:
            pass
        try:
            self._128 = add_reverse_domain('128', ip_type='4')
        except ReverseDomainExistsError, e:
            self._128 = Reverse_Domain.objects.filter( name = '128' )
            pass
        try:
             self._128._193 = add_reverse_domain('128.193', ip_type='4')
        except ReverseDomainExistsError, e:
            self._128._193 = Reverse_Domain.objects.filter( name = '128.193' )
            pass

    ######################
    ### Updating Tests ###
    ######################
    """
    Things that could go wrong.
    1) Update to an invalid ip.
    2) Update to an invalid name.
    """
    def do_update_A_record_test( self, record, new_name, new_ip ):
        update_A_record( record , new_name, new_ip )
        aret  = Address_Record.objects.filter( name = new_name ).select_relate('ip')[0]
        if new_name:
            self.assertEqual( aret.name, new_name )
        if new_ip:
            self.assertEqual( aret.ip.__str__(), new_ip )

    def do_update_AAAA_record_test( self, record, new_name, new_ip ):
        update_AAAA_record( record , new_name, new_ip )
        aret  = Address_Record.objects.filter( name = new_name ).select_relate('ip')[0]
        if new_name:
            self.assertEqual( aret.name, new_name )
        if new_ip:
            self.assertEqual( aret.ip.__str__(), new_ip )


    def test_update_A_record(self):
        rec0 = add_A_record( '', self.m_o_e , "128.193.0.1")
        rec1 = add_A_record( 'foo', self.m_o_e , "128.193.0.1")
        rec2 = add_A_record( 'bar', self.m_o_e , "128.193.0.1")
        rec3 = add_A_record( 'bazisgoingtobelasdfhklashflashfllk-324-123n2319rjn2ddasfdasfd-sa', self.m_o_e , "128.193.0.1")
        rec4 = add_A_record( 'rees', self.m_o_e , "128.193.0.1")
        self.do_update_A_record_test( rec0, "whooooop1", "128.193.23.1")
        self.do_update_A_record_test( rec1, "whoooasfdasdflasdfjoop3", "128.193.23.2")
        self.do_update_A_record_test( rec2, "whsdflhjsafdohaosdfhsadooooop1", "128.193.23.4")
        self.do_update_A_record_test( rec3, "wasdflsadhfaoshfuoiwehfjsdkfavbhooooop1", "128.193.23.3")
        self.do_update_A_record_test( rec0, "liaslfdjsa8df09823hsdljf-whooooop1", "128.193.25.17")
        self.do_update_A_record_test( rec1, "w", "128.193.29.83")
        self.do_update_A_record_test( rec0, None, "128.193.23.1")
        self.do_update_A_record_test( rec1, "whoooasfdasdflasdfjoop3", None)
        self.do_update_A_record_test( rec2, None, None)

    def test_update_AAAA_record(self):
        osu_block = "2620:105:F000:"
        rec0 = add_AAAA_record( '', self.z_o_e , osu_block+":1")
        rec1 = add_AAAA_record( 'foo', self.z_o_e , osu_block+":1")
        rec2 = add_AAAA_record( 'bar', self.z_o_e , osu_block+":1")
        self.do_update_AAAA_record_test( rec0, "whoooooasfjsp1", osu_block+"0:0:123:321::")
        self.do_update_AAAA_record_test( rec1, "wasfasfsafdhooooop1", osu_block+"0:0:123:321::")
        self.do_update_AAAA_record_test( rec2, "whoooooasfdisafsap1", osu_block+"0:24:123:322:1")
        self.do_update_AAAA_record_test( rec0, "whooooop1", osu_block+"0:aaa::1")
        self.do_update_AAAA_record_test( rec0, "wasflasksdfhooooop1", osu_block+"0:dead::")
        self.do_update_AAAA_record_test( rec1, "whooooosf13fp1", osu_block+"0:0::")
        self.do_update_AAAA_record_test( rec1, "whooooodfijasf1", osu_block+"0:1:23::")
        self.do_update_AAAA_record_test( rec2, "lliasdflsafwhooooop1", osu_block+":")
        self.do_update_AAAA_record_test( rec1, "whooooopsjafasf1", osu_block+":0::")
        self.do_update_AAAA_record_test( rec2, None, osu_block+":")
        self.do_update_AAAA_record_test( rec1, "whooooopsjafasf1", None)
        self.do_update_AAAA_record_test( rec0, None, osu_block+"0:0:123:321::")
        self.do_update_AAAA_record_test( rec1, None, osu_block+"0:0:123:321::")
        self.do_update_AAAA_record_test( rec2, None, None)

    def test_update_invalid_ip_A_record(self):
        rec0 = add_A_record( 'z', self.g_o_e , "128.193.254.1")
        try:
            self.do_update_A_record_test( rec0, None, "1928.193.23.1")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, None, 12314123)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, "narf", 1214123)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, "%asdfsaf", "1928.193.23.1")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, " sdfsa ", None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, None, "19.193.23.1.2")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, -1, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, 34871, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_A_record_test( rec0, None, 71134)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))

    def test_update_invalid_ip_AAAA_record(self):
        osu_block = "2620:105:F000:"
        rec0 = add_AAAA_record( '', self.g_o_e , osu_block+":1")
        try:
            self.do_update_AAAA_record_test( rec0, None, osu_block+":::")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_AAAA_record_test( rec0, "%asdfsaf", osu_block)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_AAAA_record_test( rec0, " sdfsa ", None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_AAAA_record_test( rec0, "sdfsa", 1239812472934623847)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_AAAA_record_test( rec0, None, "128.193.1.1")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_AAAA_record_test( rec0, -1, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_AAAA_record_test( rec0, 34871, None)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            self.do_update_AAAA_record_test( rec0, None, 71134)
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))


    ######################
    ### Removing Tests ###
    ######################
    def do_remove_A_record_test(self, aname, domain, ip ):
        ip_int= ipaddr.IPv4Address(ip).__int__()
        add_A_record( aname, domain , ip )
        aret  = Address_Record.objects.filter( name = aname )
        ipret = Ip.objects.filter( ip_lower = ip_int, ip_type='4' )
        self.assertTrue(aret)
        self.assertTrue(ipret)

        remove_A_record(aname, domain)

        aret  = Address_Record.objects.filter( name = aname )
        ipret = Ip.objects.filter( ip_lower = ip_int, ip_type='4' )
        self.assertFalse(aret)
        self.assertFalse(ipret)

    def do_remove_AAAA_record_test(self, aname, domain, ip ):
        ip_upper, ip_lower= ipv6_to_longs(ip)
        add_AAAA_record( aname, domain , ip )
        aret  = Address_Record.objects.filter( name = aname )
        ipret = Ip.objects.filter( ip_upper = ip_upper, ip_lower = ip_lower, ip_type='6' )
        self.assertTrue(aret)
        self.assertTrue(ipret)

        remove_A_record(aname, domain)

        aret  = Address_Record.objects.filter( name = aname )
        ipret = Ip.objects.filter( ip_upper = ip_upper, ip_lower = ip_lower, ip_type='6' )
        self.assertFalse(aret)
        self.assertFalse(ipret)

    def test_remove_A_address_records(self):
        self.do_remove_A_record_test("", self.o_e, "128.193.0.1" )
        self.do_remove_A_record_test("far", self.o_e, "128.193.0.2" )
        self.do_remove_A_record_test("fetched", self.o_e, "128.193.1.1" )
        self.do_remove_A_record_test("drum", self.o_e, "128.193.2.1" )
        self.do_remove_A_record_test("and", self.o_e, "128.193.0.3" )
        self.do_remove_A_record_test("bass", self.o_e, "128.193.2.2" )
        self.do_remove_A_record_test("dude", self.o_e, "128.193.5.1" )
        self.do_remove_A_record_test("man", self.o_e, "128.193.1.4" )
        self.do_remove_A_record_test("right", self.o_e, "128.193.2.6" )
        self.do_remove_A_record_test("", self.f_o_e, "128.193.0.1" )
        self.do_remove_A_record_test("far", self.f_o_e, "128.193.0.2" )
        self.do_remove_A_record_test("fetched", self.f_o_e, "128.193.1.1" )
        self.do_remove_A_record_test("drum", self.f_o_e, "128.193.2.1" )
        self.do_remove_A_record_test("and", self.f_o_e, "128.193.0.3" )
        self.do_remove_A_record_test("bass", self.f_o_e, "128.193.2.2" )
        self.do_remove_A_record_test("dude", self.f_o_e, "128.193.5.1" )
        self.do_remove_A_record_test("man", self.f_o_e, "128.193.1.4" )
        self.do_remove_A_record_test("right", self.f_o_e, "128.193.2.6" )

    def test_remove_AAAA_address_records(self):
        osu_block = "2620:105:F000:"
        self.do_remove_AAAA_record_test("", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record_test("please", self.o_e, osu_block+":2" )
        self.do_remove_AAAA_record_test("visit", self.o_e, osu_block+":4" )
        self.do_remove_AAAA_record_test("from", self.o_e, osu_block+":2" )
        self.do_remove_AAAA_record_test("either", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record_test("webpages", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record_test("read", self.o_e, osu_block+":1" )
        self.do_remove_AAAA_record_test("", self.f_o_e, osu_block+":1" )
        self.do_remove_AAAA_record_test("please", self.f_o_e, osu_block+":2" )
        self.do_remove_AAAA_record_test("visit", self.f_o_e, osu_block+":4" )
        self.do_remove_AAAA_record_test("from", self.f_o_e, osu_block+":2" )
        self.do_remove_AAAA_record_test("either", self.f_o_e, osu_block+":1" )
        self.do_remove_AAAA_record_test("webpages", self.f_o_e, osu_block+":1" )
        self.do_remove_AAAA_record_test("read", self.f_o_e, osu_block+":1" )

    def test_remove_nonexistant_A_address_records(self):
        try:
            remove_A_record("pretty_sure_it_doesn_exist0", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        #++++++++++++++++
        try:
            remove_A_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        try:
            remove_A_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        #++++++++++++++++
        try:
            remove_A_record("pretty_sure_it_doesn_exist0", self.o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        #++++++++++++++++
        try:
            remove_A_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        try:
            remove_A_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))

    def test_remove_nonexistant_AAAA_address_records(self):
        try:
            remove_AAAA_record("pretty_sure_it_doesn_exist0", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        #++++++++++++++++
        try:
            remove_AAAA_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        try:
            remove_AAAA_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        #++++++++++++++++
        try:
            remove_AAAA_record("pretty_sure_it_doesn_exist0", self.o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))
        #++++++++++++++++
        try:
            remove_AAAA_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        try:
            remove_AAAA_record("", self.f_o_e)
        except RecordNotFoundError, e:
            pass
        self.assertEqual(RecordNotFoundError, type(e))

    ####################
    ### Adding Tests ###
    ####################

    def test_add_A_address_records(self):
        add_A_record( '', self.o_e , "128.193.0.1")
        add_A_record( '', self.f_o_e , "128.193.0.6")
        add_A_record( 'ba3z', self.o_e , "128.193.0.3")
        add_A_record( 'ba3z', self.f_o_e , "128.193.0.8")
        add_A_record( 'foob1ar', self.f_o_e , "128.193.0.10")
        add_A_record( 'foob1ar', self.o_e , "128.193.0.5")
        add_A_record( 'foo', self.f_o_e , "128.193.0.7")
        add_A_record( 'foo', self.o_e , "128.193.0.2")
        add_A_record( 'ba-r', self.f_o_e , "128.193.0.9")
        add_A_record( 'ba-r', self.o_e , "128.193.0.4")
        add_A_record( 'somthingreallylongthatmightactuallybeaddedinttherealworl-r', self.o_e , "128.193.0.4")

    def test_add_AAAA_address_records(self):
        osu_block = "2620:105:F000:"
        add_AAAA_record( '', self.f_o_e , osu_block+":4")
        add_AAAA_record( '', self.o_e , osu_block+":1")
        add_AAAA_record( '6ba-r', self.o_e , osu_block+":6")
        add_AAAA_record( '6ba-r', self.f_o_e , osu_block+":7")
        add_AAAA_record( '6foo', self.f_o_e , osu_block+":5")
        add_AAAA_record( '6foo', self.o_e , osu_block+":3")
        add_AAAA_record( '6ba3z', self.o_e , osu_block+":4")
        add_AAAA_record( '6ba3z', self.f_o_e , osu_block+":6")
        add_AAAA_record( '6foob1ar', self.o_e , osu_block+":5")
        add_AAAA_record( '6foob1ar', self.f_o_e , osu_block+":8")

    def test_bad_A_ip(self):
        #IPv4 Tests
        osu_block = "2620:105:F000:"
        try:
            add_A_record( 'asdf0', self.o_e , osu_block+":1")
        except ipaddr.AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))

        try:
            add_A_record( 'asdf1', self.o_e , 123142314)
        except ipaddr.AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))

        try:
            add_A_record( 'asdf1', self.o_e , "128.193.0.1.22")
        except ipaddr.AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        try:
            add_A_record( 'asdf2', self.o_e , "128.193.8")
        except ipaddr.AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        try:
            add_A_record( 'asdf3', self.o_e , "99.193.8.1")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))

    def test_bad_AAAA_ip(self):
        # IPv6 Tests
        osu_block = "2620:105:F000:"
        try:
            add_AAAA_record( 'asdf5', self.o_e , "128.193.8.1")
        except ipaddr.AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))
        try:
            add_AAAA_record( 'asdf4', self.o_e , osu_block+":::")
        except ipaddr.AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))

        try:
            add_AAAA_record( 'asdf4', self.o_e , 123213487823762347612346)
        except ipaddr.AddressValueError, e:
            pass
        self.assertEqual(AddressValueError, type(e))

        try:
            add_AAAA_record( 'asdf6', self.o_e , "9::1")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))
        try:
            add_AAAA_record( 'asdf6', self.o_e , "9213:123:213:12::1")
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual(ReverseDomainNotFoundError, type(e))

    def test_add_A_records_exist(self):
        add_A_record( 'new', self.f_o_e,"128.193.0.2" )
        try:
            add_A_record( 'new', self.f_o_e ,"128.193.0.2" )
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))
        add_A_record( 'nope', self.o_e ,"128.193.0.2" )
        try:
            add_A_record( 'nope', self.o_e ,"128.193.0.2" )
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))

    def test_add_AAAA_records_exist(self):
        osu_block = "2620:105:F000:"
        add_AAAA_record( 'new', self.f_o_e,osu_block+":2")
        try:
            add_AAAA_record( 'new', self.f_o_e ,osu_block+":2")
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))
        add_AAAA_record( 'nope', self.o_e ,osu_block+":4")
        try:
            add_AAAA_record( 'nope', self.o_e ,osu_block+":4")
        except RecordExistsError, e:
            pass
        self.assertEqual(RecordExistsError, type(e))

    def test_add_A_invalid_address_records(self):
        try:
            add_A_record( 'foo.nas', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        self.assertEqual("Please do not span multiple domains when creating A records. Please create the nas subdomain before adding records to it.", e.__str__())

        try:
            add_A_record( 'foo.bar.nas', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        self.assertEqual("Please do not span multiple domains when creating A records. Please create subdomain(s) 'bas' and 'bar' before adding records to them/it.", e.__str__())

        try:
            add_A_record( 'foo.baz.bar.nas', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        self.assertEqual("Please do not span multiple domains when creating A records. Please create subdomain(s) 'baz', 'bar' and 'nas' before adding records to it/them.", e.__str__())

        try:
            add_A_record( 'n as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))

        try:
            add_A_record( 'n as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            add_A_record( 'n%as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            add_A_record( 'n+as', self.o_e ,"128.193.0.2" )
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))

    def test_add_AAAA_invalid_address_records(self):
        osu_block = "2620:105:F000:"
        try:
            add_AAAA_record( 'foo.nas', self.o_e , osu_block+":1")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        self.assertEqual("Please do not span multiple domains when creating A records. Please create the nas subdomain before adding records to it.", e.__str__())

        try:
            add_AAAA_record( 'foo.bar.nas', self.o_e ,osu_block+":2")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        self.assertEqual("Please do not span multiple domains when creating A records. Please create subdomain(s) 'bas' and 'bar' before adding records to them/it.", e.__str__())

        try:
            add_AAAA_record( 'foo.baz.bar.nas', self.o_e ,osu_block+":3")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        self.assertEqual("Please do not span multiple domains when creating A records. Please create subdomain(s) 'baz', 'bar' and 'nas' before adding records to it/them.", e.__str__())

        try:
            add_AAAA_record( 'n as', self.o_e ,osu_block+":4")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))

        try:
            add_AAAA_record( 'n as', self.o_e ,osu_block+":5")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            add_AAAA_record( 'n%as', self.o_e ,osu_block+":6")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
        try:
            add_AAAA_record( 'n+as', self.o_e ,osu_block+":7")
        except InvalidRecordNameError, e:
            pass
        self.assertEqual(InvalidRecordNameError, type(e))
