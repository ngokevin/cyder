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

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.cname.models import CNAME

from cyder.cydns.validation import ValidationError

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

        n_f_m = Domain.objects.get(pk=n_f_m.pk) #Refresh object
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
        d, _ = Domain.objects.get_or_create(name="gaz")
        d.soa = None
        d.save()
        d1, _ = Domain.objects.get_or_create(name="foo.gaz")
        d1.soa = s1
        d1.save()

    def test_3_soa_validators(self):
        s1, _ = SOA.objects.get_or_create(primary = "ns1.foo2.gaz", contact = "hostmaster.foo", comment="foo.gaz2")

        r, _ = ReverseDomain.objects.get_or_create(name='9')
        r.soa = s1
        r.save()

        d, _ = Domain.objects.get_or_create(name="gaz")
        d.soa = s1
        self.assertRaises(ValidationError, d.save)

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
        # Make sure deleting a domain doesn't leave stuff hanging.
        # TODO A records, Mx, TXT... all of the records!!

    def test_delegation_add_domain(self):
        name = "boom1"
        dom = Domain( name = name, delegated=True )
        dom.save()

        name = "boom.boom1"
        dom = Domain( name = name, delegated=False )
        self.assertRaises(ValidationError, dom.save)

    def test_delegation(self):
        name = "boom"
        dom = Domain( name = name, delegated=True )
        dom.save()


        # Creating objects in the domain should be locked.
        arec = AddressRecord(label="ns1", domain=dom, ip_str="128.193.99.9", ip_type='4')
        self.assertRaises(ValidationError, arec.save)

        ns = Nameserver(domain=dom, server="ns1."+dom.name)
        self.assertRaises(ValidationError, ns.save)

        cn = CNAME(label = "999asdf", domain = dom, data = "asdf.asdf")
        self.assertRaises(ValidationError, cn.save)

        # Undelegate (unlock) the domain.
        dom.delegated = False
        dom.save()

        # Add glue and ns record.
        arec.save()
        ns.save()

        # Re delegate the domain.
        dom.delegated = True
        dom.save()

        # Creation should still be locked
        arec1 = AddressRecord(label="ns2", domain=dom, ip_str="128.193.99.9", ip_type='4')
        self.assertRaises(ValidationError, arec1.save)

        ns1 = Nameserver(domain=dom, server="ns2."+dom.name)
        self.assertRaises(ValidationError, ns1.save)

        cn1 = CNAME(label = "1000asdf", domain = dom, data = "asdf.asdf")
        self.assertRaises(ValidationError, cn1.save)

        # Editing should be allowed.
        arec = AddressRecord.objects.get(pk=arec.pk)
        arec.ip_str = "129.193.88.2"
        arec.save()

    def test_existing_record_new_domain(self):
        name = "bo"
        dom = Domain.objects.get_or_create( name = name, delegated=False )
        b_dom.save()

        name = "to.bo"
        dom = Domain.objects.get_or_create( name = name, delegated=False )
        t_dom.save()

        arec1 = AddressRecord(label="no", domain=t_dom, ip_str="128.193.99.9", ip_type='4')
        arec1.save()

        name = "no.to.bo"
        n_dom = Domain( name = name, delegated=False )
        self.assertRaises(ValidationError, dom.save)

    def test_existing_cname_new_domain(self):
        name = "bo"
        dom = Domain.objects.get_or_create( name = name, delegated=False )
        b_dom.save()

        name = "to.bo"
        dom = Domain.objects.get_or_create( name = name, delegated=False )
        t_dom.save()

        ns1 = Nameserver(domain=dom, server="no."+t_dom.name)
        ns1.save()

        name = "no.to.bo"
        n_dom = Domain( name = name, delegated=False )
        self.assertRaises(ValidationError, dom.save)
