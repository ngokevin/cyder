"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cyder.cydns.reverse_domain.models import Reverse_Domain, add_reverse_ipv4_domain, add_reverse_ipv6_domain, ReverseDomainNotFoundError
from cyder.cydns.reverse_domain.models import ReverseDomainExistsError
from cyder.cydns.ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs
from cyder.cydns.domain.models import Domain, add_domain, DomainExistsError, MasterDomainNotFoundError, remove_domain, DomainNotFoundError
from cyder.cydns.domain.models import remove_domain_str, remove_domain
import ipaddr
import pdb

class SimpleTest(TestCase):
    def setUp(self):
        add_reverse_ipv4_domain('128.193', None)
        add_str_ipv4('128.193.0.4')
        self.com_domain = add_domain('com', None )

    def test_remove_domain(self):
        add_domain('foo.com', self.com_domain )
        remove_domain_str('foo.com')
        foo = add_domain('foo.com', self.com_domain )
        remove_domain(foo)

    def test_remove_nonexistent_domain(self):
        try:
            remove_domain_str('fooasdfcom')
        except DomainNotFoundError, e:
            pass
        self.assertEqual( DomainNotFoundError, type(e))

    def test__name_to_master_domain(self):
        try:
            add_domain('foo.cn', None )
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))

        cn = add_domain('cn', master_domain=None )
        add_domain('foo.cn', master_domain=cn )
        try:
            add_domain('foo.cn', master_domain=cn )
        except DomainExistsError, e:
            pass
        self.assertEqual( DomainExistsError, type(e))


    def test_create_domain(self):
        edu = add_domain('edu', master_domain=None)
        add_domain('oregonstate.edu', master_domain=edu )
        try:
            add_domain('foo.bar.oregonstate.edu', master_domain=edu )
        except MasterDomainNotFoundError, e:
            pass
        self.assertEqual( MasterDomainNotFoundError, type(e))

    def test_add_reverse_domainless_ips(self):
        try:
            add_str_ipv4('8.8.8.8')
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual( ReverseDomainNotFoundError, type(e))

        try:
            add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        except ReverseDomainNotFoundError, e:
            pass
        self.assertEqual( ReverseDomainNotFoundError, type(e))

        add_reverse_ipv6_domain('2001:0db8:85a3:0000:0000::', None)
        try:
            add_reverse_ipv6_domain('2001:0db8:85a3::', None)
        except ReverseDomainExistsError, e:
            pass
        self.assertEqual( ReverseDomainExistsError, type(e))

        add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')

    def test_ipv6_to_longs(self):
        ip = ipaddr.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        ret = ipv6_to_longs(ip.__str__())
        self.assertEqual( ret, (2306139570357600256,151930230802227))
