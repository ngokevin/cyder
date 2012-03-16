"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db import IntegrityError

from cyder.cydns.domain.models import Domain, MasterDomainNotFoundError
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.nameserver.models import Nameserver,NSRecordMisconfiguredError
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.ip.models import Ip
from cyder.cydns.cydns import InvalidRecordNameError
import pdb

class NSTests(TestCase):
    def setUp(self):
        self.r = Domain( name = "ru" )
        self.r.save()
        self.f_r = Domain( name = "foo.ru" )
        self.f_r.save()
        self.b_f_r = Domain( name = "bar.foo.ru" )
        self.b_f_r.save()

        self._128 = ReverseDomain( name = '128', ip_type= '4' )
        self._128.save()

    def do_add(self, domain, server, glue = False):
        ns = Nameserver( domain = domain, server = server)
        if glue:
            ns.glue = glue
        ns.save()
        ns.save()
        self.assertTrue(ns.__repr__())
        self.assertTrue(ns.details())
        self.assertTrue(ns.get_absolute_url())
        self.assertTrue(ns.get_edit_url())
        self.assertTrue(ns.get_delete_url())
        ret = Nameserver.objects.filter( domain = domain, server = server )
        if glue:
            fglue = AddressRecord.objects.get( pk = ns.glue.pk )
            self.assertEqual( len(ret), 1 )
        self.assertEqual( len(ret), 1 )
        return ns

    def test_add_TLD(self):
        data = { 'domain':self.r , 'server':'bar.foo.ru' }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )

    def test_add_ns(self):
        data = { 'domain':self.r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

        data = { 'domain':self.r , 'server':u'ns3.moot.ru' }
        self.do_add( **data )

        data = { 'domain':self.b_f_r , 'server':'n1.moot.ru' }
        self.do_add( **data )

        data = { 'domain':self.b_f_r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

        data = { 'domain':self.r , 'server':'asdf.asdf' }
        self.do_add( **data )

        # Test no need for glue
        ip = Ip( ip_str = '128.193.1.36', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns2', domain = self.r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.f_r , 'server':'asdf.asdf', 'glue':glue }
        self.assertRaises(NSRecordMisconfiguredError, self.do_add, **data)

    def test_add_invalid(self):
        data = { 'domain':self.f_r , 'server':'ns3.foo.ru' }
        self.assertRaises( NSRecordMisconfiguredError, self.do_add, **data  )

    def testtest_add_ns_in_domain(self):
        ip = Ip( ip_str = '128.193.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns2', domain = self.r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.r , 'server':'ns2.ru', 'glue':glue }
        ns = self.do_add( **data )
        self.assertTrue( ns.glue )
        self.assertEqual( ns.server, ns.glue.fqdn() )

        ip = Ip( ip_str = '128.193.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns3', domain = self.f_r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.f_r , 'server':'ns3.foo.ru', 'glue':glue }
        ns = self.do_add( **data )
        self.assertTrue( ns.glue )
        self.assertEqual( ns.server, ns.glue.fqdn() )

    def test_add_ns_outside_domain(self):
        data = { 'domain':self.f_r , 'server':'ns2.ru' }
        ns = self.do_add( **data )
        self.assertFalse( ns.glue )

    def test_update_glue_to_no_glue(self):
        ip = Ip( ip_str = '128.193.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns3', domain = self.r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.r , 'server':'ns3.ru', 'glue':glue }
        ns = self.do_add( **data )
        self.assertTrue( ns.glue )
        self.assertEqual( ns.server, ns.glue.fqdn() )
        ns.server = "ns3.foo.com"
        ns.glue = None
        ns.save()
        self.assertFalse( ns.glue )

        ns.server = "ns3.ru"
        ns.glue = glue
        ns.save()
        self.assertTrue( ns.glue )
        self.assertEqual( ns.server, ns.glue.fqdn() )

        ns.server = "ns4.ru"
        ns.glue = glue
        self.assertRaises(NSRecordMisconfiguredError, ns.save )



    def test_delete_ns(self):
        ip = Ip( ip_str = '128.196.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns4', domain = self.f_r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.f_r , 'server':'ns4.foo.ru', 'glue':glue }
        ns = self.do_add( **data )
        self.assertTrue( ns.glue )
        self.assertEqual( ns.server, ns.glue.fqdn() )

        ns.delete()
        nsret = Nameserver.objects.filter( server = 'ns2.foo.ru', domain = self.f_r )
        self.assertFalse( nsret )

    def test_invalid_create(self):
        ip = Ip( ip_str = '128.193.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns2', domain = self.r, ip = ip, ip_type = '4' )
        glue.save()

        data = { 'domain':self.r , 'server':'ns2 .ru', 'glue':glue }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'ns2$.ru', 'glue':glue }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'ns2..ru', 'glue':glue }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'ns2.ru ', 'glue':glue }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'domain':self.r , 'server':True, 'glue':glue }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'', 'glue':glue }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )

    def test_add_dup(self):
        data = { 'domain':self.r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

        self.assertRaises( IntegrityError, self.do_add, **data)
