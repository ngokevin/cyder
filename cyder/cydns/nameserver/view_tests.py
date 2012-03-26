from django.test import TestCase
from django.test.client import Client

from cyder.cydns.view_tests import GenericViewTests, random_label
from cyder.settings import CYDNS_BASE_URL
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.nameserver.models import Nameserver, ReverseNameserver

import pdb

class NSViewTests(TestCase):
    def setUp(self):
        url_slug = "nameserver"
        dname = random_label()
        self.client = Client()
        self.url_slug = url_slug
        self.domain, create = Domain.objects.get_or_create(name=dname)
        while not create:
            dname = "a"+dname
            self.domain, create = Domain.objects.get_or_create(name=dname)
        server = random_label()
        self.test_obj, create = Nameserver.objects.get_or_create( server=server, domain= self.domain )
        while not create:
            server = "a"+server
            self.test_obj, create = Nameserver.objects.get_or_create( server=server, domain= self.domain )

    def post_data(self):
        server = random_label()
        return {'server': server, 'domain':self.domain.pk}


builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(NSViewTests,test.__name__+"_ns", test)

class RevNSViewTests(TestCase):
    def setUp(self):
        url_slug = "reverse_nameserver"
        dname = random_label()
        self.client = Client()
        self.url_slug = url_slug
        self.domain, create = ReverseDomain.objects.get_or_create(name="255")
        server = random_label()
        self.test_obj, create = ReverseNameserver.objects.get_or_create( server=server, reverse_domain= self.domain )
        while not create:
            server = "a"+server
            self.test_obj, create = ReverseNameserver.objects.get_or_create( server=server, reverse_domain= self.domain )

    def post_data(self):
        server = random_label()
        return {'server': server, 'domain':self.domain.pk}


builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(RevNSViewTests,test.__name__+"_rev_ns", test)
