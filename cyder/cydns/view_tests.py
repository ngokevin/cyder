from django.test import TestCase
from django.test.client import Client

from cyder.settings import CYDNS_BASE_URL
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver

import pdb


class GenericViewTests(object):

    """
    An object that builds test funtions. It's super generic and quite a huge hack.
    You need to define a setUp function like this.
    def setUp(self):
        # The django client
        self.client = Client()

        # The url slug of the app being tested
        self.url_slug = "xxxxx"

        # A name of domain to use when creating records
        dname = "food"
        self.domain, create = Domain.objects.get_or_create(name=dname)
        while not create: # This ensures that a domain is created.
            dname = "a"+dname
            self.domain, create = Domain.objects.get_or_create(name=dname)

        # Make a generic test "object". This object is called self.test_obj and is used to test datail and
        # update views
        server = "random"
        self.test_obj, create = Nameserver.objects.get_or_create( server=server, domain= self.domain )
        while not create:
            server = "a"+server
            self.test_obj, create = Nameserver.objects.get_or_create( server=server, domain= self.domain )

    This function is used to generate valid data to test views that require POST data.

        def post_data(self):
            import random
            import string
            server = ''
            for i in range(random.randint(0,57)):
                server += string.letters[random.randint(0,len(string.letters)-1)]
            return {'server': server, 'domain':self.domain.pk}

    """

    def build_all_tests(self):
        return (
                self.build_get_object_delete(),\
                self.build_get_object_details(),\
                self.build_post_object_update(),\
                self.build_get_object_update(),\
                self.build_post_create_in_domain(),\
                self.build_get_create_in_domain(),\
                self.build_post_create(),\
                self.build_base_app(),\
                self.build_get_create(),\
                lambda junk: True \
                )


    # url(r'^cyder/cydns/nameserver$', NSListView.as_view() ),
    def build_base_app(self):
        def test_base_app(self):
            resp = self.client.get(CYDNS_BASE_URL+"/%s" % (self.url_slug))
            self.assertEqual(resp.status_code, 200)
        return test_base_app

    # url(r'^cyder/cydns/nameserver/create$', NSCreateView.as_view()),
    def build_get_create(self):
        def test_get_create(self):
            resp = self.client.get(CYDNS_BASE_URL+"/%s/create" % (self.url_slug))
            self.assertEqual(resp.status_code, 200)
        return test_get_create

    def build_post_create(self):
        def test_post_create(self):
            data = {"server":"1asfsadfasdf.asdfasfd.safd", "domain":self.domain.pk }
            resp = self.client.post(CYDNS_BASE_URL+"/%s/%s/create" % (self.url_slug, self.domain.pk), self.post_data())
            self.assertEqual(resp.status_code, 302)
        return test_post_create

    def build_get_create_in_domain(self):
        # url(r'^cyder/cydns/nameserver/(?P<domain>[\w-]+)/create$', NSCreateView.as_view()),
        def test_get_create_in_domain(self):
            resp = self.client.get(CYDNS_BASE_URL+"/%s/%s/create" % (self.url_slug, self.domain.pk))
            self.assertEqual(resp.status_code, 200)
        return test_get_create_in_domain

    def build_post_create_in_domain(self):
        def test_post_create_in_domain(self):
            data = {"server":"asfsadfasdf.asdfasfd.safd", "domain":self.domain.pk }
            resp = self.client.post(CYDNS_BASE_URL+"/%s/%s/create" % (self.url_slug, self.domain.pk), self.post_data())
            self.assertEqual(resp.status_code, 302)
        return test_post_create_in_domain

    def build_get_object_update(self):
        # url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/update$', NSUpdateView.as_view() ),
        def test_get_object_update(self):
            resp = self.client.get(CYDNS_BASE_URL+"/%s/%s/update" % (self.url_slug, self.test_obj.pk))
            self.assertEqual(resp.status_code, 200)
        return test_get_object_update


    def build_post_object_update(self):
        def test_post_object_update(self):
            resp = self.client.post(CYDNS_BASE_URL+"/%s/%s/create" % (self.url_slug, self.domain.pk), self.post_data())
            self.assertEqual(resp.status_code, 302)
            pass
        return test_post_object_update

    def build_get_object_details(self):
        # url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/detail$', NSDetailView.as_view() ),
        def test_get_object_details(self):
            resp = self.client.get(CYDNS_BASE_URL+"/%s/%s/detail" % (self.url_slug, self.test_obj.pk))
            self.assertEqual(resp.status_code, 200)
        return test_get_object_details

    def build_get_object_delete(self):
        # url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/delete$', NSDeleteView.as_view() )
        def test_get_object_delete(self):
            resp = self.client.get(CYDNS_BASE_URL+"/%s/%s/delete" % (self.url_slug, self.test_obj.pk))
            self.assertEqual(resp.status_code, 200)
            pass
        return test_get_object_delete



class NSViewTests(TestCase):
    def setUp(self):
        url_slug = "nameserver"
        dname = "food"
        self.client = Client()
        self.url_slug = url_slug
        self.domain, create = Domain.objects.get_or_create(name=dname)
        while not create:
            dname = "a"+dname
            self.domain, create = Domain.objects.get_or_create(name=dname)
        server = "random"
        self.test_obj, create = Nameserver.objects.get_or_create( server=server, domain= self.domain )
        while not create:
            server = "a"+server
            self.test_obj, create = Nameserver.objects.get_or_create( server=server, domain= self.domain )

    def post_data(self):
        import random
        import string
        server = ''
        """Generate valid post data"""
        for i in range(random.randint(0,57)):
            server += string.letters[random.randint(0,len(string.letters)-1)]
        return {'server': server, 'domain':self.domain.pk}

builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(NSViewTests,test.__name__, test)

