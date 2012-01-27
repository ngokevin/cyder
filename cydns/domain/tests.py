"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import Reverse_Domain, ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain

from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs, Ip

from cyder.cydns.domain.models import Domain, add_domain, DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.domain.models import remove_domain_str, remove_domain, remove_domain, DomainNotFoundError, DomainHasChildDomains, _name_to_domain

#from cyder.cydns.address_record.models import remove_domain_str, remove_domain, remove_domain, RecordExistsError
from cyder.cydns.models import InvalidRecordNameError
from cyder.cydns.cydns import trace

import ipaddr

class DomainTests(TestCase):
    def do_generic_invalid( self, name,  function, exception ):
        e = None
        try:
            function(name)
        except exception, e:
            pass
        self.assertEqual(exception, type(e))
        e.__str__()

    def test_remove_domain(self):
        add_domain('com')
        add_domain('foo.com')
        remove_domain_str('foo.com')
        foo = add_domain('foo.com' )
        foo.__str__()
        foo.__repr__()
        remove_domain(foo)

    def test_remove_nonexistent_domain(self):
        bad = 'asdfsa'
        self.do_generic_invalid(bad, remove_domain_str, DomainNotFoundError)
        bad = None
        self.do_generic_invalid(bad, remove_domain_str, InvalidRecordNameError)
        bad = True
        self.do_generic_invalid(bad, remove_domain_str, InvalidRecordNameError)
        bad = "!@#[34]"
        self.do_generic_invalid(bad, remove_domain_str, InvalidRecordNameError)
        bad = "e "
        self.do_generic_invalid(bad, remove_domain_str, InvalidRecordNameError)

    def test__name_to_master_domain(self):
        try:
            add_domain('foo.cn' )
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))
        e.__str__()
        e = None

        cn = add_domain('cn' )
        add_domain('foo.cn')
        try:
            add_domain('foo.cn')
        except DomainExistsError, e:
            pass
        self.assertEqual( DomainExistsError, type(e))
        e = None


    def test_create_domain(self):
        edu = add_domain('edu')
        add_domain('oregonstate.edu' )
        try:
            add_domain('foo.bar.oregonstate.edu' )
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))
        e = None

    def test_remove_has_child_domain(self):
        com = add_domain('com')
        f_c = add_domain('foo.com')
        b_f_c = add_domain('boo.foo.com')
        bad = 'foo.com'
        self.do_generic_invalid(bad, remove_domain_str, DomainHasChildDomains)

    def test_invalid_add(self):
        bad = 12324
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)
        bad = "asfda.asdf"
        self.do_generic_invalid(bad, add_domain, MasterDomainNotFoundError)
        bad = "asfda.as df"
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)
        bad = "."
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)
        bad = "edu. "
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)
        bad = None
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)
        bad = True
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)
        bad = False
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)
        bad = "!@#$"
        self.do_generic_invalid(bad, add_domain, InvalidRecordNameError)

    def test_remove_has_child_records(self):
        pass
        # TODO
        # A records, Mx, TXT... all of the records!!
