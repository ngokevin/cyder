"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import pdb

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client

from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.middleware.authentication import AuthenticationMiddleware
from cyder.middleware.dev_authentication import DevAuthenticationMiddleware

class CtnrPermissionsTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        # test user is for tests only
        self.test_user = User.objects.get_or_create(username='test_user', password='test_user')[0]

        # development user exists as fixture, has admin to all ctnrs
        self.dev_user = User.objects.get(username='development')

        # create container where user has no admin
        self.ctnr = Ctnr(id=None)
        self.ctnr.save()
        self.ctnr_user = CtnrUser(id=None, ctnr=self.ctnr, user=self.test_user, is_admin=0)
        self.ctnr_user.save()

        # create container where user has admin
        self.ctnr_admin = Ctnr(id=None)
        self.ctnr_admin.save()
        self.ctnr_user_admin = CtnrUser(id=None, ctnr=self.ctnr_admin, user=self.test_user, is_admin=1)
        self.ctnr_user_admin.save()

    def test_session_has_ctnr_dev(self):
        """
        Test middleware sets session ctnr on log in
        Precondition: no session container
        Postcondition: session container
        """
        request = HttpRequest()
        request.user = AnonymousUser()
        request.session = {}

        dev_middleware = DevAuthenticationMiddleware()
        dev_middleware.process_request(request)

        self.assertTrue('ctnr' in request.session)

    def test_ctnr_domain_user(self):
        """
        Test being in ctnr /w domain /wo admin gives only read perm to domain
        Precondition: domain in ctnr, user does not have admin to ctnr
        Postcondition: user has only read access to that domain
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = {'ctnr': self.ctnr}

        # create domain, add domain to ctnr
        domain = Domain(id=None, name='foo')
        domain.save()

        self.ctnr.domains.add(domain)
        self.ctnr.save()

        has_perm = self.test_user.get_profile().has_perm(request, domain, write=False)
        self.assertTrue(has_perm, 'user should have read access')

        has_perm = self.test_user.get_profile().has_perm(request, domain, write=True)
        self.assertFalse(has_perm, 'user should not have write access')

    def test_ctnr_domain_admin(self):
        """
        Test being in ctnr /w domain /w admin gives full perm to that domain
        Precondition: domain in ctnr, user has admin to ctnr
        Postcondition: user has full access to that domain
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = {'ctnr': self.ctnr_admin}

        # create domain, add domain to ctnr
        domain = Domain(id=None, name='foo')
        domain.save()
        self.ctnr_admin.domains.add(domain)
        self.ctnr_admin.save()

        has_perm = self.test_user.get_profile().has_perm(request, domain, write=False)
        self.assertTrue(has_perm, 'user should have read access')

        has_perm = self.test_user.get_profile().has_perm(request, domain, write=True)
        self.assertTrue(has_perm, 'user should have write access')

    def test_ctnr_reverse_domain_user(self):
        """
        Test being in ctnr /w rdomain /wo admin gives only read perm to rdomain
        Precondition: rdomain in ctnr, user does not have admin to ctnr
        Postcondition: user has only read access to that rdomain
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = {'ctnr': self.ctnr}

        # create reverse domain, add reverse domain to ctnr
        rdomain = ReverseDomain(id=None, name='128')
        rdomain.save()

        self.ctnr.reverse_domains.add(rdomain)
        self.ctnr.save()

        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=False)
        self.assertTrue(has_perm, 'user should have read access')

        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=True)
        self.assertFalse(has_perm, 'user should not have write access')
