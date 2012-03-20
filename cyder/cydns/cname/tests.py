"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cyder.cydns.cname.models import CNAME
from cyder.cydns.soa.models import SOA
from cyder.cydns.domain.models import Domain
from cyder.cydns.cydns import InvalidRecordNameError
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import pdb


class CNAMETests(TestCase):

    def setUp(self):
        primary = "ns5.oregonstate.edu"
        contact = "admin.oregonstate.edu"
        retry = 1234
        refresh = 1234123
        self.soa = SOA( primary = primary, contact = contact, retry = retry, refresh = refresh)
        self.soa.save()

        self.g = Domain( name = "gz" )
        self.g.save()
        self.c_g = Domain( name = "coo.gz" )
        self.c_g.soa = self.soa
        self.c_g.save()
        self.d = Domain( name = "dz" )
        self.d.save()


    def do_add(self, label, domain, data):
        cn = CNAME( label = label, domain = domain, data = data )
        cn.save()
        cn.save()
        self.assertTrue(cn.get_absolute_url())
        self.assertTrue(cn.get_edit_url())
        self.assertTrue(cn.get_delete_url())
        self.assertTrue(cn.details())

        cs = CNAME.objects.filter( label = label, domain = domain, data = data )
        self.assertEqual( len(cs), 1)
        return cn

    def test_add(self):
        label = "foo"
        domain = self.g
        data = "foo.com"
        x = self.do_add( label, domain, data )

        label = "boo"
        domain = self.c_g
        data = "foo.foo.com"
        self.do_add( label, domain, data )

        label = "fo1"
        domain = self.g
        data = "foo.com"
        self.do_add( label, domain, data )
        self.assertRaises(ValidationError, self.do_add, *( label, domain, data ))

        label = ""
        domain = self.g
        data = "foo.com"
        self.do_add( label, domain, data )

    def test_soa_condition(self):
        label = ""
        domain = self.c_g
        data = "foo.com"
        self.assertRaises(ValidationError, self.do_add, *( label, domain, data ))

    def test_data_domain(self):
        label = "fo1"
        domain = self.g
        data = "foo.dz"
        cn = self.do_add( label, domain, data )

        self.assertTrue( self.d == cn.data_domain )

    def test_add_bad(self):
        label = ""
        domain = self.g
        data = "..foo.com"
        self.assertRaises(ValidationError, self.do_add, *( label, domain, data ))
