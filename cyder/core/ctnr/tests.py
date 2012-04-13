from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client


class BasicCtnrTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.request = HttpRequest()
        self.request.session = SessionStore()

    def test_session_has_ctnr_dev(self):
        """
        Test middleware sets session ctnr on log in
        Precondition: no session container
        Postcondition: session container
        """
        self.request.user = AnonymousUser()

        dev_middleware = DevAuthenticationMiddleware()
        dev_middleware.process_request(self.request)

        self.assertTrue('ctnr' in self.request.session)
