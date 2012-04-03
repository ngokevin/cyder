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
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.txt.models import TXT
from cyder.cydns.srv.models import SRV
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

        # create container that is meant to stay empty
        self.ctnr_empty = Ctnr(id=None)
        self.ctnr_empty.save()
        self.ctnr_user_empty = CtnrUser(id=None, ctnr=self.ctnr_empty, user=self.test_user, is_admin=1)
        self.ctnr_user_empty.save()

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

    def test_ctnr_domain(self):
        """
        Test being in ctnr /w domain gives appropriate perms
        Precondition: domain in ctnr
        Postcondition: has full perm to domain if admin, read only if not
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = {'ctnr': self.ctnr}

        # create domain, add domain to ctnr
        domain = Domain(id=None, name='foo')
        domain.save()

        self.ctnr.domains.add(domain)
        self.ctnr.save()

        self.ctnr_admin.domains.add(domain)
        self.ctnr_admin.save()

        # checks where user is not admin
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=False)
        self.assertTrue(has_perm, 'user should have read access')
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=True)
        self.assertFalse(has_perm, 'user should not have write access')

        # checks where user is admin
        request.session = {'ctnr': self.ctnr_admin}
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=False)
        self.assertTrue(has_perm, 'user should have read access')
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=True)
        self.assertTrue(has_perm, 'user should have write access')

        # checks where obj not in ctnr
        request.session = {'ctnr': self.ctnr_empty}
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=False)
        self.assertFalse(has_perm, 'user should not have read access')
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=True)
        self.assertFalse(has_perm, 'user should not have write access')

    def test_ctnr_reverse_domain(self):
        """
        Test being in ctnr /w rdomain gives appropriate perms
        Precondition: rdomain in ctnr
        Postcondition: full perm if admin, read only if not
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = {'ctnr': self.ctnr}

        # create reverse domain, add reverse domain to ctnr
        rdomain = ReverseDomain(id=None, name='128')
        rdomain.save()

        self.ctnr.reverse_domains.add(rdomain)
        self.ctnr.save()

        self.ctnr_admin.reverse_domains.add(rdomain)
        self.ctnr_admin.save()

        # checks where user is not admin
        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=False)
        self.assertTrue(has_perm, 'user should have read access')
        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=True)
        self.assertFalse(has_perm, 'user should not have write access')

        # checks where user is admin
        request.session = {'ctnr': self.ctnr_admin}
        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=False)
        self.assertTrue(has_perm, 'user should have read access')
        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=True)
        self.assertTrue(has_perm, 'user should have write access')

        # checks where obj not in ctnr
        request.session = {'ctnr': self.ctnr_empty}
        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=False)
        self.assertFalse(has_perm, 'user should not have read access')
        has_perm = self.test_user.get_profile().has_perm(request, rdomain, write=True)
        self.assertFalse(has_perm, 'user should not have write access')

    def test_ctnr_domain_records(self):
        """
        Test being in ctnr /w common domain records gives appropriate perms
        common domain records: cname, mx, txt, srv
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = {'ctnr': self.ctnr}

        # create domain, add domain to ctnr
        domain = Domain(id=None, name='foo')
        domain.save()

        domain_records = []
        domain_records.append(CNAME(domain=domain))
        domain_records.append(MX(domain=domain))
        domain_records.append(TXT(domain=domain))
        domain_records.append(SRV(domain=domain))

        for record in domain_records:
            # checks where user is not admin
            has_perm = self.test_user.get_profile().has_perm(request, record, write=False)
            self.assertTrue(has_perm, 'user should have read access')
            has_perm = self.test_user.get_profile().has_perm(request, record, write=True)
            self.assertFalse(has_perm, 'user should not have write access')

            # checks where user is admin
            request.session = {'ctnr': self.ctnr_admin}
            has_perm = self.test_user.get_profile().has_perm(request, record, write=False)
            self.assertTrue(has_perm, 'user should have read access')
            has_perm = self.test_user.get_profile().has_perm(request, record, write=True)
            self.assertTrue(has_perm, 'user should have write access')

            # checks where obj not in ctnr
            request.session = {'ctnr': self.ctnr_empty}
            has_perm = self.test_user.get_profile().has_perm(request, record, write=False)
            self.assertFalse(has_perm, 'user should not have read access')
            has_perm = self.test_user.get_profile().has_perm(request, record, write=True)
            self.assertFalse(has_perm, 'user should not have write access')
