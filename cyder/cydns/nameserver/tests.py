"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.ip.models import Ip
import pdb

class NSTestsModels(TestCase):
    def setUp(self):
        self.r = Domain( name = "ru" )
        self.r.save()
        self.f_r = Domain( name = "foo.ru" )
        self.f_r.save()
        self.b_f_r = Domain( name = "bar.foo.ru" )
        self.b_f_r.save()

        self.f = Domain( name = "fam" )
        self.f.save()

        self._128 = ReverseDomain( name = '128', ip_type= '4' )
        self._128.save()

    def do_add(self, domain, server):
        ns = Nameserver( domain = domain, server = server)
        ns.save()
        ns.save()
        self.assertTrue(ns.__repr__())
        self.assertTrue(ns.details())
        self.assertTrue(ns.get_absolute_url())
        self.assertTrue(ns.get_edit_url())
        self.assertTrue(ns.get_delete_url())
        ret = Nameserver.objects.filter( domain = domain, server = server )
        self.assertEqual( len(ret), 1 )
        return ns

    def test_add_TLD(self):
        data = { 'domain':self.r , 'server':'bar.foo.ru' }
        self.assertRaises( ValidationError, self.do_add, **data )

    def test_add_ns(self):
        data = { 'domain':self.r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

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

    def test_add_invalid(self):
        data = { 'domain':self.f_r , 'server':'ns3.foo.ru' }
        self.assertRaises( ValidationError, self.do_add, **data  )

    def testtest_add_ns_in_domain(self):
        ip = Ip( ip_str = '128.193.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns2', domain = self.r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.r , 'server':'ns2.ru' }
        ns = self.do_add( **data )
        self.assertTrue( ns.glue )
        self.assertEqual( ns.server, ns.glue.fqdn() )

        ip = Ip( ip_str = '128.193.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns3', domain = self.f_r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.f_r , 'server':'ns3.foo.ru' }
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
        data = { 'domain':self.r , 'server':'ns3.ru' }
        ns = self.do_add( **data )
        self.assertTrue( ns.glue )

        ns.server = "ns4.wee"
        ns.save()
        self.assertTrue( ns.glue == None )



    def test_delete_ns(self):
        ip = Ip( ip_str = '128.196.1.10', ip_type = '4' )
        ip.save()
        glue = AddressRecord( label='ns4', domain = self.f_r, ip = ip, ip_type='4' )
        glue.save()
        data = { 'domain':self.f_r , 'server':'ns4.foo.ru' }
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

        data = { 'domain':self.r , 'server':'ns2 .ru' }
        self.assertRaises( ValidationError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'ns2$.ru' }
        self.assertRaises( ValidationError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'ns2..ru' }
        self.assertRaises( ValidationError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'ns2.ru ' }
        self.assertRaises( ValidationError, self.do_add, **data )
        data = { 'domain':self.r , 'server':'' }
        self.assertRaises( ValidationError, self.do_add, **data )

    def test_add_dup(self):
        data = { 'domain':self.r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

        self.assertRaises( ValidationError, self.do_add, **data)
