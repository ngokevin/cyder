"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain


class CNAMETest(TestCase):

    def setUp(self):
        self.g = Domain( name = "gz" )
        self.g.save()
        self.c_g = Domain( name = "coo.gz" )
        self.c_g.save()
        self.d = Domain( name = "dz" )
        self.d.save()


    def do_add(self, label, domain, data):
        cn = CNAME( label = label, domain = domain, data = data )
        cn.save()

        cs = CNAME.objects.filter( label = label, domain = domain, data = data )
        self.assertEqual( len(cs), 1)
        return cn

    def test_add(self):
        label = "foo"
        domain = self.g
        data = "foo.com"
        self.do_add( label, domain, data )

        label = "boo"
        domain = self.c_g
        data = "foo.foo.com"
        self.do_add( label, domain, data )

        label = "fo1"
        domain = self.g
        data = "foo.com"
        self.do_add( label, domain, data )

    def test_data_domain(self):
        label = "fo1"
        domain = self.g
        data = "foo.dz"
        cn = self.do_add( label, domain, data )

        self.assertTrue( self.d == cn.data_domain )

