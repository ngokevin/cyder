"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cyder.cydns.reverse_domain.models import Reverse_Domain, add_reverse_domain, ReverseDomainNotFoundError
from ip.models import add_str_ipv4, add_str_ipv6, ipv6_to_longs
import ipaddr

class SimpleTest(TestCase):
    def setUp(self):
        add_reverse_domain('128.193', None)
        add_str_ipv4('128.193.0.4')

    def test_add_reverse_domainless_ips(self):
        try:
            add_str_ipv4('8.8.8.8')
        except ReverseDomainNotFoundError, e:
            print "ReverseDomainNotFound caught correctly."

        try:
            add_str_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        except ReverseDomainNotFoundError, e:
            print "ReverseDomainNotFound caught correctly."

    def test_ipv6_to_longs(self):
        ip = ipaddr.IPv6Address('2001:0db8:85a3:0000:0000:8a2e:0370:733')
        ret = ipv6_to_longs(ip.__str__())
        self.assertEqual( ret, (2306139570357600256,151930230802227))
