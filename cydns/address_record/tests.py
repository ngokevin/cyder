"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cyder.cydns.cydns import trace

from cyder.cydns.reverse_domain.models import ReverseDomain, ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.ip.models import Ip, ipv6_to_longs

from cyder.cydns.domain.models import Domain, DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.domain.models import DomainNotFoundError

from cyder.cydns.models import InvalidRecordNameError, CyAddressValueError
from cyder.cydns.address_record.models import RecordNotFoundError
from cyder.cydns.address_record.models import AddressRecord,RecordExistsError

import ipaddr
import pdb

class AddressRecordTests(TestCase):
    def setUp(self):
        self.osu_block = "633:105:F000:"
        boot_strap_add_ipv6_reverse_domain("0.6.3")
        try:
            self.e = Domain( name='edu' )
            self.e.save()
        except DomainExistsError, e:
            pass
        try:
            self.o_e = Domain( name='oregonstate.edu' )
            self.o_e.save()
        except DomainExistsError, e:
            self.o_e = Domain.objects.filter( name = 'oregonstate.edu' )[0]
            pass

        try:
            self.f_o_e = Domain( name='foo.oregonstate.edu' )
            self.f_o_e.save()
        except DomainExistsError, e:
            self.f_o_e = Domain.objects.filter( name = 'foo.oregonstate.edu' )[0]
            pass

        try:
            self.m_o_e = Domain( name= 'max.oregonstate.edu')
            self.m_o_e.save()
        except DomainExistsError, e:
            self.m_o_e = Domain.objects.filter( name = 'max.oregonstate.edu' )[0]
            pass

        try:
            self.z_o_e = Domain( name='zax.oregonstate.edu')
            self.z_o_e.save()
        except DomainExistsError, e:
            self.z_o_e = Domain.objects.filter( name = 'zax.oregonstate.edu' )[0]
            pass
        try:
            self.g_o_e = Domain( name='george.oregonstate.edu')
            self.g_o_e.save()
        except DomainExistsError, e:
            self.g_o_e = Domain.objects.filter( name = 'george.oregonstate.edu' )[0]
            pass

        try:
            self._128 = ReverseDomain(name='128')
            self._128.save()
        except ReverseDomainExistsError, e:
            self._128 = ReverseDomain.objects.filter( name = '128' )[0]
            pass

        try:
             self._128_193 = ReverseDomain( name = '128.193')
             self._128_193.save()
        except ReverseDomainExistsError, e:
            self._128_193 = ReverseDomain.objects.filter( name = '128.193' )[0]
            pass

    ######################
    ### Updating Tests ###
    ######################
    def test_invalid_update_to_existing(self):

        osu_block = "633:105:F000:"
        data = {'label': 'bar','domain': self.z_o_e ,'ip': "128.193.40.1"}
        test_ip1 = Ip(ip_str =data['ip'], ip_type='4')
        test_ip1.save()
        data = {'label': 'bar','domain': self.z_o_e ,'ip': "128.193.40.2"}
        test_ip2 = Ip(ip_str =data['ip'], ip_type='4')
        test_ip2.save()
        data = {'label': 'bar','domain': self.z_o_e ,'ip': "128.193.40.1"}
        test_ip3 = Ip(ip_str =data['ip'], ip_type='4')
        test_ip3.save()
        rec1 = AddressRecord( label='bar', domain= self.z_o_e , ip=test_ip1, ip_type='4')
        rec2 = AddressRecord( label='bar', domain= self.z_o_e , ip=test_ip2, ip_type='4')
        rec3 = AddressRecord( label='foo', domain= self.z_o_e , ip=test_ip3, ip_type='4')
        rec3.save()
        rec2.save()
        rec1.save()

        rec1.label = "foo"
        self.assertRaises(RecordExistsError,rec1.save)

        rec3.label = "bar"
        self.assertRaises(RecordExistsError,rec3.save)

        test_ip4 = Ip(ip_str =osu_block+":1", ip_type='6')
        test_ip4.save()
        test_ip5 = Ip(ip_str =osu_block+":2", ip_type='6')
        test_ip5.save()
        test_ip6 = Ip(ip_str =osu_block+":1", ip_type='6')
        test_ip6.save()

        rec1 = AddressRecord( label='bar', domain=self.z_o_e , ip = test_ip4, ip_type='6')
        rec2 = AddressRecord( label='bar', domain=self.z_o_e , ip = test_ip5, ip_type='6')
        rec3 = AddressRecord( label='foo', domain=self.z_o_e , ip = test_ip6, ip_type='6')
        rec1.save()
        rec2.save()
        rec3.save()

        data = { 'A_record':rec2, 'new_ip':osu_block+":1"}
        rec2.ip.ip_str = data['new_ip']
        rec2.ip.save()
        self.assertRaises(RecordExistsError,rec2.save)

        rec3.label = 'bar'
        self.assertRaises(RecordExistsError,rec3.save)

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
            aret  = AddressRecord.objects.filter( label = new_name, ip__ip_upper = ip_upper,\
                                             ip__ip_lower = ip_lower, ip__ip_type = ip_type).\
                                             select_related('ip')[0]
        elif new_name:
            # Just new_name
            aret  = AddressRecord.objects.filter( label = new_name, ip__ip_upper = ip_upper,\
                                             ip__ip_lower = ip_lower, ip__ip_type = ip_type).\
                                             select_related('ip')[0]
        else:
            # Just new_ip
            aret  = AddressRecord.objects.filter( label = record.label, ip__ip_upper = ip_upper,\
                                             ip__ip_lower = ip_lower, ip__ip_type = ip_type).\
                                             select_related('ip')[0]
        if new_name:
            self.assertEqual( aret.label, new_name )
        if new_ip:
            if ip_type == '4':
                self.assertEqual( aret.ip.__str__(), ipaddr.IPv4Address(new_ip).__str__() )
            else:
                self.assertEqual( aret.ip.__str__(), ipaddr.IPv6Address(new_ip).__str__() )

    def do_update_A_record( self, record, new_name, new_ip ):
        if new_name:
            record.label = new_name
        if new_ip:
            record.ip.ip_str = new_ip
            record.ip.save()
        record.save()
        self._do_generic_update_test( record, new_name, new_ip, '4' )

    def do_update_AAAA_record( self, record, new_name, new_ip ):
        if new_name:
            record.label = new_name
        if new_ip:
            record.ip.ip_str = new_ip
            record.ip.save()
        record.save()
        self._do_generic_update_test( record, new_name, new_ip, '6' )


    def test_update_A_record(self):
        test_ip = Ip( ip_str = "128.193.0.1", ip_type = '4' )
        test_ip.save()
        rec0 = AddressRecord( label = '',domain= self.m_o_e , ip = test_ip , ip_type='4')
        rec0.save()

        test_ip1 = Ip( ip_str = "128.193.0.1", ip_type = '4' )
        test_ip1.save()
        rec1 = AddressRecord( label = 'foo',domain= self.m_o_e , ip = test_ip1 , ip_type='4')
        rec1.save()

        test_ip2 = Ip( ip_str = "128.193.0.1", ip_type = '4' )
        test_ip2.save()
        rec2 = AddressRecord( label = 'bar',domain= self.m_o_e , ip = test_ip2 , ip_type='4')
        rec2.save()

        test_ip3 = Ip( ip_str = "128.193.0.1", ip_type = '4' )
        test_ip3.save()
        rec3 = AddressRecord( label ='bazisgoingtobelasdfhklashflashfllk-324-123n2319rjn2ddasfdasfd-sa', domain= self.m_o_e , ip = test_ip3 , ip_type='4')
        rec3.save()

        self.do_update_A_record( rec0, "whooooop1", "128.193.23.1")
        self.do_update_A_record( rec1, "whoooasfdasdflasdfjoop3", "128.193.23.2")
        self.do_update_A_record( rec2, "whsdflhjsafdohaosdfhsadooooop1", "128.193.23.4")
        self.do_update_A_record( rec3, "wasdflsadhfaoshfuoiwehfjsdkfavbhooooop1", "128.193.23.3")
        self.do_update_A_record( rec0, "liaslfdjsa8df09823hsdljf-whooooop1", "128.193.25.17")
        self.do_update_A_record( rec1, "w", "128.193.29.83")
        self.do_update_A_record( rec0, None, "128.193.23.1")
        self.do_update_A_record( rec1, "whoooasfdasdflasdfjoop3", None)

    def test_update_AAAA_record(self):
        boot_strap_add_ipv6_reverse_domain("8.6.2.0")
        osu_block = "8620:105:F000:"
        test_ip = Ip( ip_str=osu_block+":1", ip_type='6')
        test_ip.save()
        rec0 = AddressRecord( label='', domain=self.z_o_e ,ip=test_ip, ip_type='6')
        test_ip1 = Ip( ip_str=osu_block+":1", ip_type='6')
        test_ip1.save()
        rec1 = AddressRecord( label='foo', domain=self.z_o_e ,ip=test_ip1, ip_type='6')

        test_ip2 = Ip( ip_str=osu_block+":1", ip_type='6')
        test_ip2.save()
        rec2 = AddressRecord( label='bar', domain=self.z_o_e ,ip=test_ip2, ip_type='6')

        self.do_update_AAAA_record( rec0, "whoooooasfjsp1", osu_block+"0:0:123:321::")
        self.do_update_AAAA_record( rec1, "wasfasfsafdhooooop1", osu_block+"0:0:123:321::")
        self.do_update_AAAA_record( rec2, "whoooooasfdisafsap1", osu_block+"0:24:123:322:1")
        self.do_update_AAAA_record( rec0, "whooooop1", osu_block+"0:aaa::1")
        self.do_update_AAAA_record( rec0, "wasflasksdfhooooop1", osu_block+"0:dead::")
        self.do_update_AAAA_record( rec1, "whooooosf13fp1", osu_block+"0:0::")
        self.do_update_AAAA_record( rec1, "whooooodfijasf1", osu_block+"0:1:23::")
        self.do_update_AAAA_record( rec2, "lliasdflsafwhooooop1", osu_block+":")
        self.do_update_AAAA_record( rec1, "whooooopsjafasf1", osu_block+"0::")
        self.do_update_AAAA_record( rec1, None, osu_block+"0:0:123:321::")

    def test_update_invalid_ip_A_record(self):
        test_ip = Ip( ip_str = "128.193.23.1", ip_type = '4' )
        test_ip.save()
        rec0 = AddressRecord( label = '',domain= self.m_o_e , ip = test_ip , ip_type='4')

        test_ip1 = Ip( ip_str = "128.193.26.7", ip_type = '4' )
        test_ip1.save()
        rec1 = AddressRecord( label = 'foo',domain= self.m_o_e , ip = test_ip , ip_type='4')
        # BAD Names
        self.assertRaises( InvalidRecordNameError,self.do_update_A_record,**{'record': rec1,'new_name': ".","new_ip": None})
        self.assertRaises( InvalidRecordNameError,self.do_update_A_record,**{'record': rec0,'new_name': " sdfsa ","new_ip": None})
        self.assertRaises( InvalidRecordNameError,self.do_update_A_record,**{'record': rec0,'new_name': -1,"new_ip": None})
        self.assertRaises( InvalidRecordNameError,self.do_update_A_record,**{'record': rec0,'new_name': 34871,"new_ip": None})
        self.assertRaises( InvalidRecordNameError,self.do_update_A_record,**{'record': rec0,'new_name': "asdf.","new_ip": None})

        # BAD IPs
        self.assertRaises( CyAddressValueError,self.do_update_A_record,**{'record': rec0,'new_name': None,"new_ip": 71134})
        self.assertRaises( CyAddressValueError,self.do_update_A_record,**{'record': rec0,'new_name': None,"new_ip": "19.193.23.1.2"})
        self.assertRaises( CyAddressValueError,self.do_update_A_record,**{'record': rec0,'new_name': None,"new_ip": 12314123})
        self.assertRaises( CyAddressValueError,self.do_update_A_record,**{'record': rec0,'new_name': "narf","new_ip": 1214123})
        self.assertRaises( CyAddressValueError,self.do_update_A_record,**{'record': rec0,'new_name': "%asdfsaf","new_ip": "1928.193.23.1"})
        self.assertRaises( CyAddressValueError,self.do_update_A_record,**{'record': rec0,'new_name': None,"new_ip": "1928.193.23.1"})

        self.assertRaises( ReverseDomainNotFoundError,self.do_update_A_record,**{'record': rec0,'new_name': "asdfa","new_ip": "88.67.67.67"})

    def test_update_invalid_ip_AAAA_record(self):
        osu_block = "7620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("7.6.2.0")
        test_ip1 = Ip( ip_str=osu_block+":1", ip_type='6')
        test_ip1.save()
        rec1 = AddressRecord( label='foo', domain=self.z_o_e ,ip=test_ip1, ip_type='6')

        test_ip0 = Ip( ip_str=osu_block+":1", ip_type='6')
        test_ip0.save()
        rec0 = AddressRecord( label='foo', domain=self.z_o_e ,ip=test_ip0, ip_type='6')

        #self.assertRaises( InvalidRecordNameError,self.do_update_AAAA_record( rec1, "foo", osu_block+":1"))
        #self.assertRaises( InvalidRecordNameError,self.do_update_AAAA_record, { rec1, "george", osu_block+":1"})
        self.assertRaises( CyAddressValueError,self.do_update_AAAA_record,**{ 'record':rec0, 'new_name':None, 'new_ip':71134})
        self.assertRaises( CyAddressValueError,self.do_update_AAAA_record, **{'record': rec0,'new_name': None,'new_ip': osu_block+":::"})
        self.assertRaises( CyAddressValueError,self.do_update_AAAA_record, **{'record': rec0,'new_name': "%asdfsaf",'new_ip': osu_block})
        self.assertRaises( CyAddressValueError,self.do_update_AAAA_record, **{'record': rec0,'new_name': "sdfsa",'new_ip': 1239812472934623847})
        self.assertRaises( CyAddressValueError,self.do_update_AAAA_record, **{'record': rec0,'new_name': None,'new_ip': "128.193.1.1"})
        self.assertRaises( InvalidRecordNameError,self.do_update_AAAA_record, **{'record': rec0,'new_name': -1,'new_ip': None})
        self.assertRaises( InvalidRecordNameError,self.do_update_AAAA_record, **{'record': rec0,'new_name': "%asdfsaf",'new_ip': osu_block+":1"})
        self.assertRaises( InvalidRecordNameError,self.do_update_AAAA_record, **{'record': rec0,'new_name': " sdfsa ",'new_ip': None})

        self.assertRaises( ReverseDomainNotFoundError,self.do_update_AAAA_record, **{'record': rec0,'new_name': "asdfa",'new_ip': "6435:234:"+":1"})


    ######################
    ### Removing Tests ###
    ######################
    def do_remove_A_record(self, aname, domain, ip ):
        ip = Ip( ip_str = ip, ip_type = '4' )
        ip.save()
        aret = AddressRecord( label = aname, domain=domain, ip=ip, ip_type='4')
        aret.save()
        ipret = Ip.objects.filter( ip_lower = aret.ip.ip_lower, ip_type='4' )
        self.assertTrue(aret)
        self.assertTrue(ipret)

        aret.delete()

        aret  = AddressRecord.objects.filter( label = aname, domain = domain, ip = ipret )
        npret = Ip.objects.filter( ip_lower = ip.ip_lower, ip_type='4' )
        self.assertFalse(aret)
        self.assertFalse(npret)

    def do_remove_AAAA_record(self, aname, domain, ip ):
        ip = Ip( ip_str = ip, ip_type = '6' )
        ip.save()
        aret = AddressRecord( label = aname, domain=domain, ip=ip, ip_type='6')
        aret.save()
        ipret = Ip.objects.filter( ip_upper = aret.ip.ip_upper, ip_lower = aret.ip.ip_lower, ip_type='6' )
        self.assertTrue(aret)
        self.assertTrue(ipret)

        aret.delete()

        nret  = AddressRecord.objects.filter( label = aname, domain = domain, ip = ipret )
        npret = Ip.objects.filter( ip_upper = ip.ip_upper, ip_lower = ip.ip_lower, ip_type='6' )
        self.assertFalse(nret)
        self.assertFalse(npret)


    def test_remove_A_address_records(self):
        self.do_remove_A_record("", self.o_e, "128.193.10.1" )
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


    ####################
    ### Adding Tests ###
    ####################
    def do_add_record(self, data):
        ip = Ip(ip_str=data['ip'], ip_type = '4')
        ip.save()
        rec = AddressRecord(label = data['label'], domain=data['domain'], ip_type='4')
        rec.ip = ip
        rec.save()

        search = AddressRecord.objects.filter( label = data['label'], domain = data['domain'], ip_type='4' )
        found = False
        for record in search:
            if record.ip.__str__() == ip.__str__():
                found = True
        self.assertTrue(found)

    def do_add_record6(self, data):
        ip = Ip(ip_str=data['ip'], ip_type='6')
        ip.save()
        rec = AddressRecord(label = data['label'], domain=data['domain'], ip_type='6')
        rec.ip = ip
        rec.save()

        search = AddressRecord.objects.filter( label = data['label'], domain = data['domain'], ip_type='6' )
        found = False
        for record in search:
            if record.ip.__str__() == ip.__str__():
                found = True
        self.assertTrue(found)


    def test_add_A_address_records(self):
        ip = Ip( ip_str= "128.193.0.1", ip_type='4')
        rec = AddressRecord( label = '', domain = self.o_e ,ip=ip, ip_type='4')
        self.assertEqual( rec.__str__(), "oregonstate.edu A 128.193.0.1" )

        data = {'label': 'foob1ar','domain': self.f_o_e ,'ip': "128.193.0.10"}
        self.do_add_record( data )

        data = {'label': 'foob1ar','domain': self.o_e ,'ip': "128.193.0.5"}
        self.do_add_record( data )
        data = {'label': 'foo2','domain': self.f_o_e ,'ip': "128.193.0.7"}
        self.do_add_record( data )
        data = {'label': 'foo2','domain': self.o_e ,'ip': "128.193.0.2"}
        self.do_add_record( data )
        data = {'label': 'ba-r','domain': self.f_o_e ,'ip': "128.193.0.9"}
        self.do_add_record( data )
        data = {'label': 'ba-r','domain': self.o_e ,'ip': "128.193.0.4"}
        self.do_add_record( data )

    def test_add_AAAA_address_records(self):
        osu_block = "2620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("2.6.2.0")
        data = {'label': '','domain': self.f_o_e ,'ip': osu_block+":4"}
        self.do_add_record6( data )
        data = {'label': '','domain': self.o_e ,'ip': osu_block+":1"}
        self.do_add_record6( data )
        data = {'label': '6ba-r','domain': self.o_e ,'ip': osu_block+":6"}
        self.do_add_record6( data )
        data = {'label': '6ba-r','domain': self.f_o_e ,'ip': osu_block+":7"}
        self.do_add_record6( data )
        data = {'label': '6foo','domain': self.f_o_e ,'ip': osu_block+":5"}
        self.do_add_record6( data )
        data = {'label': '6foo','domain': self.o_e ,'ip': osu_block+":3"}
        self.do_add_record6( data )
        data = {'label': '6ba3z','domain': self.o_e ,'ip': osu_block+":4"}
        self.do_add_record6( data )
        data = {'label': '6ba3z','domain': self.f_o_e ,'ip': osu_block+":6"}
        self.do_add_record6( data )
        data = {'label': '6foob1ar','domain': self.o_e ,'ip': osu_block+":5"}
        self.do_add_record6( data )
        data = {'label': '6foob1ar','domain': self.f_o_e ,'ip': osu_block+":8"}
        self.do_add_record6( data )
        data = {'label': '23412341253254243','domain': self.f_o_e ,'ip': osu_block+":8"}
        self.do_add_record6( data )

    def test_bad_A_ip(self):
        #IPv4 Tests
        osu_block = "2620:105:F000:"
        data = {'label': 'asdf0','domain': self.o_e ,'ip': osu_block+":1"}
        self.assertRaises(CyAddressValueError ,self.do_add_record,data)

        data = {'label': 'asdf1','domain': self.o_e ,'ip': 123142314}
        self.assertRaises(CyAddressValueError ,self.do_add_record,data)

        data = {'label': 'asdf1','domain': self.o_e ,'ip': "128.193.0.1.22"}
        self.assertRaises(CyAddressValueError ,self.do_add_record,data)

        data = {'label': 'asdf2','domain': self.o_e ,'ip': "128.193.8"}
        self.assertRaises(CyAddressValueError ,self.do_add_record,data)

        data = {'label': 'asdf3','domain': self.o_e ,'ip': "99.193.8.1"}
        self.assertRaises(ReverseDomainNotFoundError ,self.do_add_record, data)

    def test_bad_AAAA_ip(self):
        # IPv6 Tests
        osu_block = "2620:105:F000:"
        data = {'label': 'asdf5','domain': self.o_e ,'ip': "128.193.8.1"}
        self.assertRaises(CyAddressValueError ,self.do_add_record6, data)
        data = {'label': 'asdf4','domain': self.o_e ,'ip': osu_block+":::"}
        self.assertRaises(CyAddressValueError ,self.do_add_record6, data)

        data = {'label': 'asdf4','domain': self.o_e ,'ip': 123213487823762347612346}
        self.assertRaises(CyAddressValueError ,self.do_add_record6,data)

        data = {'label': 'asdf6','domain': self.o_e ,'ip': "1009::1"}
        self.assertRaises(ReverseDomainNotFoundError ,self.do_add_record6, data)
        data = {'label': 'asdf6','domain': self.o_e ,'ip': "9213:123:213:12::1"}
        self.assertRaises(ReverseDomainNotFoundError ,self.do_add_record6, data)

    def test_add_A_records_exist(self):
        data = {'label': '','domain': self.f_o_e ,'ip':"128.193.0.2" }
        self.do_add_record(data)
        self.assertRaises(RecordExistsError ,self.do_add_record,data)


        data = {'label': 'new','domain': self.f_o_e ,'ip':"128.193.0.2" }
        self.do_add_record(data)
        self.assertRaises(RecordExistsError ,self.do_add_record,data)


    def test_add_AAAA_records_exist(self):
        osu_block = "9620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("9.6.2.0")

        data = {'label': 'new','domain': self.f_o_e ,'ip':osu_block+":2"}
        self.do_add_record6(data)
        self.assertRaises(RecordExistsError ,self.do_add_record6,data)

        data = {'label': 'new','domain': self.f_o_e ,'ip':osu_block+":0:9"}
        self.do_add_record6(data)
        self.assertRaises(RecordExistsError ,self.do_add_record6,data)


        data = {'label': 'nope','domain': self.o_e ,'ip':osu_block+":4"}
        self.do_add_record6(data)
        self.assertRaises(RecordExistsError ,self.do_add_record6,data)

    def test_add_A_invalid_address_records(self):

        data = {'label': "oregonstate",'domain': self.e,'ip': "128.193.0.2"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': "foo",'domain': self.o_e,'ip': "128.193.0.2"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': 'foo.nas','domain': self.o_e ,'ip':"128.193.0.2" }
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': 'foo.bar.nas','domain': self.o_e ,'ip':"128.193.0.2" }
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': 'foo.baz.bar.nas','domain': self.o_e ,'ip':"128.193.0.2" }
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': 'n as','domain': self.o_e ,'ip':"128.193.0.2" }
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': 'n as','domain': self.o_e ,'ip':"128.193.0.2" }
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': 'n%as','domain': self.o_e ,'ip':"128.193.0.2" }
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

        data = {'label': 'n+as','domain': self.o_e ,'ip':"128.193.0.2" }
        self.assertRaises(InvalidRecordNameError ,self.do_add_record, data)

    def test_add_AAAA_invalid_address_records(self):
        osu_block = "3620:105:F000:"
        boot_strap_add_ipv6_reverse_domain("3.6.2.0")

        data = {'label': 'foo.nas','domain': self.o_e ,'ip': osu_block+":1"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record6, data)

        data = {'label': 'foo.bar.nas','domain': self.o_e ,'ip':osu_block+":2"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record6, data)

        data = {'label': 'foo.baz.bar.nas','domain': self.o_e ,'ip':osu_block+":3"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record6, data)

        data = {'label': 'n as','domain': self.o_e ,'ip':osu_block+":4"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record6, data)

        data = {'label': 'n!+/*&%$#@as','domain': self.o_e ,'ip':osu_block+":5"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record6, data)

        data = {'label': 'n%as','domain': self.o_e ,'ip':osu_block+":6"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record6, data)

        data = {'label': 'n+as','domain': self.o_e ,'ip':osu_block+":7"}
        self.assertRaises(InvalidRecordNameError ,self.do_add_record6, data)
