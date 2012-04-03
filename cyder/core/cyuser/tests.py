"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client

from cyder.middleware.dev_authentication import DevAuthenticationMiddleware

class AuthenticationTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.dev_middleware = DevAuthenticationMiddleware()

    def test_session_has_ctnr_dev(self):
        """
        Test development middleware logs on development user
        Precondition: anonymous
        Postcondition: logged in as development
        """
        request = HttpRequest()
        request.user = AnonymousUser()
        request.session = {}

        self.dev_middleware.process_request(request)

        self.assertTrue(str(request.user) is not 'AnonymousUser')
