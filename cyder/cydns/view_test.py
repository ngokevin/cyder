from django.test import TestCase
from django.test.client import Client
from django.shortcuts import get_or_create

from cyder.settings import CYDNS_BASE_URL
from cyder.cydns.domain.models import Domain



class GenericViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.app = "nameserver"
        self.domain = Domain.objects.get_or_create(name="randomly-generated")

    # url(r'^cyder/cydns/nameserver$', NSListView.as_view() ),
    def test_base_app(self):
        resp = client.get(CYDNS_BASE_URL+"/%s" % (self.app))
        self.assertEqual(resp.status_code, 200)

    # url(r'^cyder/cydns/nameserver/create$', NSCreateView.as_view()),
    def test_get_create(self):
        resp = client.get(CYDNS_BASE_URL+"/%s/create" % (self.app))
        self.assertEqual(resp.status_code, 200)

    # url(r'^cyder/cydns/nameserver/(?P<domain>[\w-]+)/create$', NSCreateView.as_view()),
    def test_get_create_in_domain(self):
        resp = client.get(CYDNS_BASE_URL+"/%s/%s/create" % (self.app, self.domain.pk))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_in_domain(self):
        data = {server="asfsadfasdf.asdfasfd.safd", "domain":self.domain.pk }
        resp = client.post(CYDNS_BASE_URL+"/%s/%s/create" % (self.app, self.domain.pk), data)
        self.assertEqual(resp.status_code, 200)

    # url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/update$', NSUpdateView.as_view() ),
    def test_get_object_update(self):
        pass

    def test_post_object_update(self):
        pass

    # url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/detail$', NSDetailView.as_view() ),
    def test_get_object_details(self):
        pass

    # url(r'^cyder/cydns/nameserver/(?P<pk>[\w-]+)/delete$', NSDeleteView.as_view() )
    def test_get_object_delete(self):
        pass
