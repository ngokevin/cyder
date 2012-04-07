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

from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.nameserver.models import Nameserver
from cyder.cydns.nameserver.reverse_nameserver.models import ReverseNameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.txt.models import TXT
from cyder.cydns.soa.models import SOA
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
        self.ctnr = Ctnr(id=None, name="no_admin")
        self.ctnr.save()
        self.ctnr_user = CtnrUser(id=None, ctnr=self.ctnr, user=self.test_user, level=0)
        self.ctnr_user.save()

        # create container where user has admin
        self.ctnr_admin = Ctnr(id=None, name="has_admin")
        self.ctnr_admin.save()
        self.ctnr_user_admin = CtnrUser(id=None, ctnr=self.ctnr_admin, user=self.test_user, level=1)
        self.ctnr_user_admin.save()

        # create container that is meant to stay empty
        self.ctnr_empty = Ctnr(id=None, name="empty")
        self.ctnr_empty.save()
        self.ctnr_user_empty = CtnrUser(id=None, ctnr=self.ctnr_empty, user=self.test_user, level=1)
        self.ctnr_user_empty.save()

    def test_session_has_ctnr_dev(self):
        """
        Test middleware sets session ctnr on log in
        Precondition: no session container
        Postcondition: session container
        """
        request = HttpRequest()
        request.user = AnonymousUser()
        request.session = SessionStore()

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
        request.session = SessionStore()
        request.session['ctnr'] = self.ctnr

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
        request.session['ctnr'] = self.ctnr_admin
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=False)
        self.assertTrue(has_perm, 'user should have read access')
        has_perm = self.test_user.get_profile().has_perm(request, domain, write=True)
        self.assertTrue(has_perm, 'user should have write access')

        # checks where obj not in ctnr
        request.session['ctnr'] = self.ctnr_empty
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
        request.session = SessionStore()
        request.session['ctnr'] = self.ctnr

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
        request.session = SessionStore()
        request.session['ctnr'] = self.ctnr

        # create domain, add domain to ctnr
        domain = Domain(id=None, name='foo')
        domain.save()

        self.ctnr.domains.add(domain)
        self.ctnr.save()

        self.ctnr_admin.domains.add(domain)
        self.ctnr_admin.save()

        domain_records = []
        domain_records.append(AddressRecord(domain=domain))
        domain_records.append(CNAME(domain=domain))
        domain_records.append(MX(domain=domain))
        domain_records.append(Nameserver(domain=domain))
        domain_records.append(SRV(domain=domain))
        domain_records.append(TXT(domain=domain))

        for record in domain_records:
            # checks where user is not admin
            request.session = {'ctnr': self.ctnr}
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

    def test_ctnr_rdomain_records(self):
        """
        Test being in ctnr /w common domain records gives appropriate perms
        common domain records: cname, mx, txt, srv
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = SessionStore()
        request.session['ctnr'] = self.ctnr

        # create domain, add domain to ctnr
        rdomain = ReverseDomain(id=None, name='128')
        rdomain.save()

        self.ctnr.reverse_domains.add(rdomain)
        self.ctnr.save()

        self.ctnr_admin.reverse_domains.add(rdomain)
        self.ctnr_admin.save()

        rdomain_records = []
        rdomain_records.append(PTR(reverse_domain=rdomain))
        rdomain_records.append(ReverseNameserver(reverse_domain=rdomain))

        for record in rdomain_records:
            # checks where user is not admin
            request.session = {'ctnr': self.ctnr}
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

    def test_ctnr_rdomain_records(self):
        """
        Test being in ctnr /w common domain records gives appropriate perms
        common domain records: cname, mx, txt, srv
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = SessionStore()
        request.session['ctnr'] = self.ctnr

        # create domain, add domain to ctnr
        rdomain = ReverseDomain(id=None, name='128')
        rdomain.save()

        self.ctnr.reverse_domains.add(rdomain)
        self.ctnr.save()

        self.ctnr_admin.reverse_domains.add(rdomain)
        self.ctnr_admin.save()

        rdomain_records = []
        rdomain_records.append(PTR(reverse_domain=rdomain))
        rdomain_records.append(ReverseNameserver(reverse_domain=rdomain))

        for record in rdomain_records:
            # checks where user is not admin
            request.session = {'ctnr': self.ctnr}
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

    def test_ctnr_soa(self):
        """
        Test being in ctnr /w soa record gives appropriate perms
        """
        request = HttpRequest()
        request.user = self.test_user
        request.session = SessionStore()
        request.session['ctnr'] = self.ctnr

        # create domain with soa, add domain to ctnr
        soa = SOA()
        soa.primary = '192.168.1.1'
        soa.contact = '192.168.1.1'
        soa.save()

        domain = Domain(id=None, name='foo')
        domain.soa = soa
        domain.save()

        self.ctnr.domains.add(domain)
        self.ctnr.save()

        self.ctnr_admin.domains.add(domain)
        self.ctnr_admin.save()

        # checks where user is not admin
        has_perm = self.test_user.get_profile().has_perm(request, soa, write=False)
        self.assertTrue(has_perm, 'user should have read access')
        has_perm = self.test_user.get_profile().has_perm(request, soa, write=True)
        self.assertFalse(has_perm, 'user should not have write access')

        # checks where user is admin
        request.session = {'ctnr': self.ctnr_admin}
        has_perm = self.test_user.get_profile().has_perm(request, soa, write=False)
        self.assertTrue(has_perm, 'user should have read access')
        has_perm = self.test_user.get_profile().has_perm(request, soa, write=True)
        self.assertTrue(has_perm, 'user should have write access')

        # checks where obj not in ctnr
        request.session = {'ctnr': self.ctnr_empty}
        has_perm = self.test_user.get_profile().has_perm(request, soa, write=False)
        self.assertFalse(has_perm, 'user should not have read access')
        has_perm = self.test_user.get_profile().has_perm(request, soa, write=True)
        self.assertFalse(has_perm, 'user should not have write access')
