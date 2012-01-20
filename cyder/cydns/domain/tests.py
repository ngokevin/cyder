"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from cyder.cydns.reverse_domain.models import Reverse_Domain, add_reverse_domain,ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError,MasterReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import boot_strap_add_ipv6_reverse_domain,remove_reverse_domain

from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs, Ip

from cyder.cydns.domain.models import Domain, add_domain, DomainExistsError, MasterDomainNotFoundError
from cyder.cydns.domain.models import remove_domain_str, remove_domain, remove_domain, DomainNotFoundError

#from cyder.cydns.address_record.models import remove_domain_str, remove_domain, remove_domain, RecordExistsError
from cyder.cydns.address_record.models import InvalidRecordNameError

import ipaddr

class DomainTests(TestCase):
    def test_remove_domain(self):
        add_domain('com')
        add_domain('foo.com')
        remove_domain_str('foo.com')
        foo = add_domain('foo.com' )
        remove_domain(foo)

    def test_remove_nonexistent_domain(self):
        try:
            remove_domain_str('fooasdfcom')
        except DomainNotFoundError, e:
            pass
        self.assertEqual( DomainNotFoundError, type(e))
        e = None

    def test__name_to_master_domain(self):
        try:
            add_domain('foo.cn' )
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))
        e = None

        cn = add_domain('cn' )
        add_domain('foo.cn' )
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
