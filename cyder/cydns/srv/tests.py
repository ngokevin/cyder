"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cyder.cydns.cydns import RecordExistsError, InvalidRecordNameError
from cyder.cydns.srv.models import SRV
from cyder.cydns.domain.models import Domain


class SimpleTest(TestCase):
    def setUp(self):
        self.o = Domain( name = "org" )
        self.o.save()
        self.o_e = Domain( name = "oregonstate.org")
        self.o_e.save()
        self.b_o_e = Domain( name = "bar.oregonstate.org")
        self.b_o_e.save()

    def do_generic_add(self, data ):
        srv = SRV( **data )
        srv.__repr__()
        srv.save()
        rsrv = SRV.objects.filter( **data )
        self.assertTrue( len(rsrv) == 1 )
        return srv

    def do_remove(self, data):
        mx = self.do_generic_add( data )
        mx.delete()
        rmx = SRV.objects.filter( **data )
        self.assertTrue( len(rmx) == 0 )

    def test_add_remove_mx(self):
        data = { 'label':'_df' ,'domain':self.o_e ,'target':'relay.oregonstate.edu' ,'priority':2 ,'weight':2222 , 'port': 222 }
        self.do_remove( data )
        data = { 'label':'_' ,'domain':self.o ,'target':'foo.com.nar' ,'priority':1234 ,'weight':23414 , 'port': 222 }
        self.do_remove( data )
        data = { 'label':'_sasfd' ,'domain':self.b_o_e ,'target':'foo.safasdlcom.nar' ,'priority':12234 ,'weight':23414 , 'port': 222 }
        self.do_remove( data )
        data = { 'label':'_faf' ,'domain':self.o ,'target':'foo.com.nar' ,'priority':1234 ,'weight':23414 , 'port': 222 }
        self.do_remove( data )

    def test_invalid_add_update(self):
        data = { 'label':'_df' ,'domain':self.o_e ,'target':'relay.oregonstate.edu' ,'priority':2 ,'weight':2222 , 'port': 222 }
        srv0 = self.do_generic_add( data )
        self.assertRaises( RecordExistsError, self.do_generic_add, data )
        data = { 'label':'_df' ,'domain':self.o_e ,'target':'foo.oregonstate.edu' ,'priority':2 ,'weight':2222 , 'port': 222 }
        srv1 = self.do_generic_add( data )
        self.assertRaises( RecordExistsError, self.do_generic_add, data )

        srv0.target = "foo.oregonstate.edu"
        self.assertRaises( RecordExistsError, srv0.save )

        srv0.port = 65536
        self.assertRaises( InvalidRecordNameError, srv0.save )
        srv0.port = 1

        srv0.priority = 65536
        self.assertRaises( InvalidRecordNameError, srv0.save )
        srv0.priority = 1

        srv0.weight = 65536
        self.assertRaises( InvalidRecordNameError, srv0.save )
        srv0.weight = 1

        srv0.target = 123
        self.assertRaises( InvalidRecordNameError, srv0.save )
        srv0.target = "asdfas"

        srv0.label = "no_first"
        self.assertRaises( InvalidRecordNameError, srv0.save )
        srv0.target = "_df"


