"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client

from cyder.middleware.dev_authentication import DevAuthenticationMiddleware

class AuthenticationTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.dev_middleware = DevAuthenticationMiddleware()

    def test_dev_middleware_login(self):
        """
        Test development middleware logs on development user
        Precondition: anonymous
        Postcondition: logged in as development
        """
        request = HttpRequest()
        request.user = AnonymousUser()
        request.session = SessionStore()

        self.dev_middleware.process_request(request)

        self.assertTrue(str(request.user) is not 'AnonymousUser')

    def test_user_profile_create(self):
        """
        Test that user profile is created on user creation
        Precondition: new user created
        Postcondition: user profile created
        """
        user = User(username='user_profile_test', password='user_profile_test')
        user.save()
        try:
            self.assertTrue(user.get_profile())
        except:
            self.fail("DoesNotExist: user profile was not created on user creation")
