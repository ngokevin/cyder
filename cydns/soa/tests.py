"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cyder.cydns.soa.models import *
from cyder.cydns.models import _do_generic_invalid

class SOATest(TestCase):
    def setUp(self):
        pass

    def do_generic_add(self, primary, contact, retry, refresh):
        add_soa(primary, contact,retry, refresh)
        soa = SOA.objects.filter( primary = primary, contact = contact, retry = retry, refresh=refresh )
        self.assertTrue( len(soa) == 1 )
        return soa

    def test_add_soa(self):
        primary = "ns1.oregonstate.edu"
        contact = "admin.oregonstate.edu"
        retry = 1234
        refresh = 1234123
        self.do_generic_add(primary, contact,retry, refresh)
        primary = "do.com"
        contact = "admf.asdf"
        retry = 432152
        refresh = 1235146134
        self.do_generic_add(primary, contact,retry, refresh)

    def test_add_remove(self):
        primary = "ns1.oregonstate.edu"
        contact = "admin.oregonstate.edu"
        retry = 1234
        refresh = 1234123
        soa = self.do_generic_add(primary, contact,retry, refresh)
        remove_soa( soa )
        soa = SOA.objects.filter( primary = primary, contact = contact, retry = retry, refresh=refresh )
        self.assertTrue( len(soa) == 0 )

        primary = "do.com"
        contact = "admf.asdf"
        retry = 432152
        refresh = 1235146134
        soa = self.do_generic_add(primary, contact,retry, refresh)
        remove_soa( soa )
        soa = SOA.objects.filter( primary = primary, contact = contact, retry = retry, refresh=refresh )
        self.assertTrue( len(soa) == 0 )
