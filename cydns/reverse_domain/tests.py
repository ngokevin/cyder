"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


from cyder.cydns.reverse_domain.models import Reverse_Domain, ReverseDomainNotFoundError,ReverseChildDomainExistsError
from cyder.cydns.reverse_domain.models import add_reverse_ipv4_domain, remove_reverse_ipv4_domain
from cyder.cydns.reverse_domain.models import add_reverse_ipv6_domain, remove_reverse_ipv6_domain
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs, Ip

from cyder.cydns.domain.models import Domain, add_domain, DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.domain.models import remove_domain_str, remove_domain, remove_domain, DomainNotFoundError

#from cyder.cydns.address_record.models import remove_domain_str, remove_domain, remove_domain, RecordExistsError
from cyder.cydns.models import InvalidRecordNameError
from cyder.cydns.cydns import trace

import ipaddr
import pdb



class ReverseDomainTests(TestCase):

    # Reverse Domain test functions

    def test_remove_reverse_domain(self):
        add_reverse_ipv4_domain('127')
        rd1 = add_reverse_ipv4_domain('127.193')
        rd1.__repr__()
        rd1.__str__()
        rd2 = add_reverse_ipv4_domain('127.193.8')
        rd2.__repr__()
        rd2.__str__()
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

    def do_generic_invalid_operation( self, dname, ip_type, exception, function ):
        e = None
        try:
            if ip_type == '4':
                function(dname)
            else:
                function(dname, ip_type)
        except exception, e:
            pass
        self.assertEqual(exception, type(e))


    def test_remove_invalid_reverse_domain(self):
        rd1 = add_reverse_ipv4_domain('130')
        rd2 = add_reverse_ipv4_domain('130.193')
        rd3 = add_reverse_ipv4_domain('130.193.8')
        try:
            remove_reverse_ipv4_domain('130')
        except ReverseChildDomainExistsError, e:
            pass
        self.assertEqual( ReverseChildDomainExistsError, type(e))
    def test_master_reverse_domain(self):
        rd1 = add_reverse_ipv4_domain('128')
        rd2 = add_reverse_ipv4_domain('128.193')
        rd3 = add_reverse_ipv4_domain('128.193.8')
        self.assertEqual( rd3.master_reverse_domain, rd2 )
        self.assertEqual( rd2.master_reverse_domain, rd1 )
        self.assertEqual( rd1.master_reverse_domain, None )



    def test_add_reverse_domains(self):
        try:
            add_reverse_ipv4_domain('192.168')
        except MasterReverseDomainNotFoundError, e:
            pass
        self.assertEqual( MasterReverseDomainNotFoundError, type(e))
        e = None
        add_reverse_ipv4_domain('192')
        add_reverse_ipv4_domain('192.168')
        try:
            add_reverse_ipv4_domain('192.168')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual(ReverseDomainExistsError, type(e))
        e = None

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

    def test_boot_strap_add_ipv6_domain(self):
        osu_block = "2.6.2.1.1.0.5.F.0.0.0"
        test_dname = osu_block+".d.e.a.d.b.e.e.f"
        boot_strap_add_ipv6_reverse_domain( test_dname )
        try:
            add_reverse_ipv6_domain('2.6.2.1.1.0.5.f.0.0.0')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        e = None
        try:
            add_reverse_ipv6_domain('2.6.2.1')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        e = None
        try:
            add_reverse_ipv6_domain('2.6.2.1.1.0.5.F.0.0.0.d.e.a.d')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        e = None
        try:
            add_reverse_ipv6_domain('2.6.2.1.1.0.5.F.0.0.0.d.e.a.d.b.e.e.f')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        e = None
        try:
            add_reverse_ipv6_domain(test_dname)
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        e = None
        # These should pass
        boot_strap_add_ipv6_reverse_domain('7.6.2.4')
        boot_strap_add_ipv6_reverse_domain('6.6.2.5.1')
        # These are pretty unrealistic since they prodtrude into the host part of the address.
        boot_strap_add_ipv6_reverse_domain('4.6.2.2.1.0.5.3.f.0.0.0.1.2.3.4.1.2.3.4.1.2.3.4.1.2.3.4.1.2.3.4')
        boot_strap_add_ipv6_reverse_domain('5.6.2.3.1.0.5.3.f.0.0.0.1.2.3.4.1.2.3.4.1.2.3.4')

    def test_add_reverse_domainless_ips(self):
        try:
            add_str_ipv4('8.8.8.8')
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual( ReverseDomainNotFoundError, type(e))
        e = None

        try:
            add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual( ReverseDomainNotFoundError, type(e))
        e = None
        rd0 = boot_strap_add_ipv6_reverse_domain("2.0.0.1")
        try:
            add_reverse_ipv6_domain('2.0.0.1')
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))
        e = None
        add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')

    def test_ipv6_to_longs(self):
        ip = ipaddr.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        ret = ipv6_to_longs(ip.__str__())
        self.assertEqual( ret, (2306139570357600256,151930230802227))


    def test_add_remove_reverse_ipv6_domains(self):
        osu_block = "2620:105:F000"
        rd0 = boot_strap_add_ipv6_reverse_domain("2.6.2.0.0.1.0.5.f.0.0.0")
        ip1 = add_str_ipv6(osu_block+":8000::1")
        self.assertEqual( ip1.reverse_domain, rd0 )
        ip2 = add_str_ipv6(osu_block+":8000::2")
        self.assertEqual( ip2.reverse_domain, rd0 )
        ip3 = add_str_ipv6(osu_block+":8000::3")
        self.assertEqual( ip3.reverse_domain, rd0 )
        ip4 = add_str_ipv6(osu_block+":8000::4")
        rd1 = add_reverse_ipv6_domain("2.6.2.0.0.1.0.5.f.0.0.0.8")
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

        remove_reverse_ipv6_domain("2.6.2.0.0.1.0.5.F.0.0.0.8")

        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::1")
        ip1 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip1.reverse_domain, rd0 )
        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::2")
        ip2 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip2.reverse_domain, rd0 )
        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::3")
        ip3 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip3.reverse_domain, rd0 )
        ip_upper, ip_lower = ipv6_to_longs(osu_block+":8000::4")
        ip4 = Ip.objects.filter(ip_upper = ip_upper, ip_lower = ip_lower , ip_type = '6')[0]
        self.assertEqual( ip4.reverse_domain, rd0 )


    def test_master_reverse_ipv6_domains(self):
        rds = []
        rds.append(add_reverse_ipv6_domain('1'))
        rds.append(add_reverse_ipv6_domain('1.2'))
        rds.append(add_reverse_ipv6_domain('1.2.8'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0.0'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0.0.3'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0.0.3.2'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0.0.3.2.1'))
        rds.append(add_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0.0.0.0.0.0.0.0.0.0.0.3.2.1.3'))
        for rd in list(enumerate(rds)):
            if rd[0] == 0:
                self.assertEqual( rd[1].master_reverse_domain, None )
            else:
                self.assertEqual( rd[1].master_reverse_domain, rds[rd[0]-1] )

        try:
            remove_reverse_ipv6_domain('1.2.8.3.0.0.0.0.4.3.4.5.6.6.5.6.7.0.0')
        except ReverseChildDomainExistsError, e:
            pass
        self.assertEqual( ReverseChildDomainExistsError, type(e))
