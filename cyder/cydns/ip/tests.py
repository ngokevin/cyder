"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import ipaddr
from cyder.cydns.ip.models import ipv6_to_longs

class SimpleTest(TestCase):
    def test_add_reverse_domain(self):
        self.assertTrue(False)
