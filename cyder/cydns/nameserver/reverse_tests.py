"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from cyder.cydns.domain.models import Domain, DomainExistsError, MasterDomainNotFoundError, DomainNotFoundError
from cyder.cydns.address_record.models import AddressRecord,RecordExistsError, RecordNotFoundError
from cyder.cydns.nameserver.models import ReverseNameserver,NSRecordMisconfiguredError
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.ip.models import Ip
from cyder.cydns.cydns import RecordExistsError, InvalidRecordNameError
import pdb

class RevNSTests(TestCase):
    def setUp(self):
        self.r = ReverseDomain( name = '129', ip_type= '4' )
        self.r.save()
        self.f_r =ReverseDomain( name = '129.123', ip_type= '4' )
        self.f_r.save()
        self.b_f_r = ReverseDomain( name = '129.123.123', ip_type= '4' )
        self.b_f_r.save()
        self._128 = ReverseDomain( name = '128', ip_type= '4' )
        self._128.save()

    def do_add(self, reverse_domain, server ):
        ns = ReverseNameserver( reverse_domain = reverse_domain, server = server)
        ns.save()
        ns.save()
        self.assertTrue(ns.__repr__())
        self.assertTrue(ns.details())
        self.assertTrue(ns.get_absolute_url())
        self.assertTrue(ns.get_edit_url())
        self.assertTrue(ns.get_delete_url())
        ret = ReverseNameserver.objects.filter( reverse_domain = reverse_domain, server = server )
        self.assertEqual( len(ret), 1 )
        return ns


    def test_add_ns(self):
        data = { 'reverse_domain':self.r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

        data = { 'reverse_domain':self.r , 'server':u'ns3.moot.ru' }
        self.do_add( **data )

        data = { 'reverse_domain':self.b_f_r , 'server':'n1.moot.ru' }
        self.do_add( **data )

        data = { 'reverse_domain':self.b_f_r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

        data = { 'reverse_domain':self.r , 'server':'asdf.asdf' }
        self.do_add( **data )



    def test_add_ns_outside_reverse_domain(self):
        data = { 'reverse_domain':self.f_r , 'server':'ns2.ru' }
        ns = self.do_add( **data )



    def test_invalid_create(self):
        ip = Ip( ip_str = '128.193.1.10', ip_type = '4' )
        ip.save()

        data = { 'reverse_domain':self.r , 'server':'ns2 .ru', }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'reverse_domain':self.r , 'server':'ns2$.ru', }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'reverse_domain':self.r , 'server':'ns2..ru', }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'reverse_domain':self.r , 'server':'ns2.ru ', }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'reverse_domain':self.r , 'server':True, }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )
        data = { 'reverse_domain':self.r , 'server':'', }
        self.assertRaises( InvalidRecordNameError, self.do_add, **data )

    def test_add_dup(self):
        data = { 'reverse_domain':self.r , 'server':'ns2.moot.ru' }
        self.do_add( **data )

        self.assertRaises( RecordExistsError, self.do_add, **data)
