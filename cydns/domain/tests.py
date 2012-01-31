"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import ReverseDomain, ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.ip.models import ipv6_to_longs, Ip

from cyder.cydns.domain.models import Domain, DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.domain.models import DomainNotFoundError, DomainHasChildDomains, _name_to_domain

from cyder.cydns.models import InvalidRecordNameError
from cyder.cydns.cydns import trace

import ipaddr
import pdb

class DomainTests(TestCase):

    def test_remove_domain(self):
        c = Domain( name = 'com')
        c.save()
        f_c = Domain( name = 'foo.com')
        f_c.save()
        f_c.delete()
        foo = Domain( name = 'foo.com' )
        foo.__str__()
        foo.__repr__()

    def test_add_domain(self):
        c = Domain( name = 'com')
        c.save()

        f_c = Domain( name = 'foo.com')
        f_c.save()
        self.assertTrue( f_c.master_domain == c)

        b_c = Domain( name = 'bar.com')
        b_c.save()
        self.assertTrue( b_c.master_domain == c)

        b_b_c = Domain( name = 'baz.bar.com')
        b_b_c.save()
        self.assertTrue( b_b_c.master_domain == b_c)



    def test__name_to_master_domain(self):
        try:
            Domain( name = 'foo.cn' ).save()
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))
        e.__str__()
        e = None

        Domain( name = 'cn' ).save()
        Domain( name = 'foo.cn').save()
        try:
            Domain( name = 'foo.cn').save()
        except DomainExistsError, e:
            pass
        self.assertEqual( DomainExistsError, type(e))
        e = None


    def test_create_domain(self):
        edu = Domain( name = 'edu')
        Domain( name = 'oregonstate.edu' )
        try:
            Domain( name = 'foo.bar.oregonstate.edu' ).save()
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))
        e = None

    def test_remove_has_child_domain(self):
        Domain( name = 'com').save()
        f_c = Domain( name = 'foo.com')
        f_c.save()
        Domain( name = 'boo.foo.com').save()
        self.assertRaises(DomainHasChildDomains, f_c.delete)

    def test_invalid_add(self):
        bad = 12324
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

        bad = "asfda.as df"
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

        bad = "."
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

        bad = "edu. "
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

        bad = None
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

        bad = True
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

        bad = False
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

        bad = "!@#$"
        dom = Domain( name = bad )
        self.assertRaises(InvalidRecordNameError, dom.save)

    def test_remove_has_child_records(self):
        pass
        # TODO
        # A records, Mx, TXT... all of the records!!
