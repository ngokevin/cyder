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

from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.middleware.authentication import AuthenticationMiddleware
from cyder.middleware.dev_authentication import DevAuthenticationMiddleware

class CtnrPermissionsTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        # test user is for tests only
        self.test_user = User.objects.get_or_create(username='test_user')[0]

        # development user exists as fixture, has admin to all ctnrs
        self.dev_user = User.objects.get(username='development')

        # create container where user has no admin
        self.ctnr = Ctnr(id=None)
        self.ctnr.save()
        self.ctnr_user = CtnrUser(id=None, ctnr=self.ctnr, user=self.test_user, is_admin=0)

        # create container where user has admin
        self.ctnr_admin = Ctnr(id=None)
        self.ctnr_admin.save()
        self.ctnr_user_admin = CtnrUser(id=None, ctnr=self.ctnr_admin, user=self.test_user, is_admin=1)

        self.prod_middleware = AuthenticationMiddleware()
        self.dev_middleware = DevAuthenticationMiddleware()

    def test_session_has_ctnr_dev(self):
        """
        Test middleware sets session ctnr on log in
        Precondition: no session container
        Postcondition: session container
        """
        request = HttpRequest()
        request.user = AnonymousUser()
        request.session = {}

        self.dev_middleware.process_request(request)

        self.assertTrue('ctnr' in request.session)

    def test_ctnr_domain_admin(self):
        """
        Test being in ctnr /w domain /w admin gives write perm to that domain
        """
        request = HttpRequest()
