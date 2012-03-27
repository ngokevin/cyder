"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.ip.models import ipv6_to_longs, Ip

from cyder.cydns.domain.models import Domain
from cyder.cydns.domain.models import ValidationError, _name_to_domain
from cyder.cydns.soa.models import SOA


from cyder.cydns.cydns import ValidationError

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
        str(foo)
        foo.__repr__()

    def test_add_domain(self):
        c = Domain( name = 'com')
        c.save()

        f_c = Domain( name = 'foo.com')
        f_c.save()
        f_c.save()
        self.assertTrue( f_c.get_absolute_url() )
        self.assertTrue( f_c.get_edit_url() )
        self.assertTrue( f_c.get_delete_url() )
        self.assertTrue( f_c.master_domain == c)

        b_c = Domain( name = 'bar.com')
        b_c.save()
        self.assertTrue( b_c.master_domain == c)

        b_b_c = Domain( name = 'baz.bar.com')
        b_b_c.save()
        self.assertTrue( b_b_c.master_domain == b_c)

    def test_soa_validators(self):
        m = Domain( name = 'moo')
        m.save()

        f_m = Domain( name = 'foo.moo')
        f_m.save()

        n_f_m = Domain( name = 'noo.foo.moo')
        n_f_m.save()

        b_m = Domain( name = 'baz.moo')
        b_m.save()

        s = SOA( primary="ns1.foo.com", contact="asdf", comment="test")
        s.save()

        f_m.soa = s
        f_m.save()

        b_m.soa = s
        self.assertRaises(ValidationError, b_m.save)

        n_f_m.soa = s
        n_f_m.save()

        m.soa = s
        m.save()

        b_m.soa = s
        b_m.save()

        m.soa = None
        self.assertRaises(ValidationError, m.save)

        s2 = SOA( primary="ns1.foo.com", contact="asdf", comment="test2")
        s2.save()

        m.soa = s2
        self.assertRaises(ValidationError, m.save)

    def test_2_soa_validators(self):
        s1, _ = SOA.objects.get_or_create(primary = "ns1.foo.gaz", contact = "hostmaster.foo", comment="foo.gaz2")
        s2, _ = SOA.objects.get_or_create(primary = "ns1.foo.gaz", contact = "hostmaster.foo", comment="baz.gaz3")
        d, _ = Domain.objects.get_or_create(name="gaz")
        d.soa = None
        d.save()
        d1, _ = Domain.objects.get_or_create(name="foo.gaz")
        d1.soa = s1
        d1.save()




    def test__name_to_master_domain(self):
        try:
            Domain( name = 'foo.cn' ).save()
        except ValidationError, e:
            pass
        self.assertEqual( ValidationError, type(e))
        str(e)
        e = None

        Domain( name = 'cn' ).save()
        d = Domain( name = 'foo.cn')
        d.save()
        d = Domain( name = 'foo.cn')
        self.assertRaises(ValidationError, d.save)


    def test_create_domain(self):
        edu = Domain( name = 'edu')
        Domain( name = 'oregonstate.edu' )
        try:
            Domain( name = 'foo.bar.oregonstate.edu' ).save()
        except ValidationError, e:
            pass
        self.assertEqual( ValidationError, type(e))
        e = None

    def test_remove_has_child_domain(self):
        Domain( name = 'com').save()
        f_c = Domain( name = 'foo.com')
        f_c.save()
        Domain( name = 'boo.foo.com').save()
        self.assertRaises(ValidationError, f_c.delete)

    def test_invalid_add(self):

        bad = "asfda.as df"
        dom = Domain( name = bad )
        self.assertRaises(ValidationError, dom.save)

        bad = "."
        dom = Domain( name = bad )
        self.assertRaises(ValidationError, dom.save)

        bad = "edu. "
        dom = Domain( name = bad )
        self.assertRaises(ValidationError, dom.save)

        bad = ""
        dom = Domain( name = bad )
        self.assertRaises(ValidationError, dom.save)

        bad = "!@#$"
        dom = Domain( name = bad )
        self.assertRaises(ValidationError, dom.save)

    def test_remove_has_child_records(self):
        pass
        # TODO
        # A records, Mx, TXT... all of the records!!
