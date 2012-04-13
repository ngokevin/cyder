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


class PermissionsTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.test_user = User.objects.get_or_create(username='test_user', password='test_user')[0]
        self.setup_request()

        # superuser
        self.superuser = User.objects.get(username='development')

        # cyder admin
        self.cyder_admin = User.objects.get_or_create(username='cyder_admin', password='cyder_admin')[0]
        self.ctnr_global = Ctnr.objects.get(id=1)
        self.ctnr_user_cyder_admin = CtnrUser(id=None, ctnr=self.ctnr_global, user=self.cyder_admin, level=2)
        self.ctnr_user_cyder_admin.save()

        # admin
        self.ctnr_admin = Ctnr(id=None, name="admin")
        self.ctnr_admin.save()
        self.ctnr_user_admin = CtnrUser(id=None, ctnr=self.ctnr_admin, user=self.test_user, level=2)
        self.ctnr_user_admin.save()

        # user
        self.ctnr_user = Ctnr(id=None, name="user")
        self.ctnr_user.save()
        self.ctnr_user_user = CtnrUser(id=None, ctnr=self.ctnr_user, user=self.test_user, level=1)
        self.ctnr_user_user.save()

        # guest
        self.ctnr_guest = Ctnr(id=None, name="guest")
        self.ctnr_guest.save()
        self.ctnr_user_guest = CtnrUser(id=None, ctnr=self.ctnr_guest, user=self.test_user, level=0)
        self.ctnr_user_guest.save()

        # pleb
        self.pleb_user = User.objects.get_or_create(username='pleb_user', password='pleb_user')[0]

    def test_soa_perms(self):
        """
        Test SOA perms
        """
        self.setup_request()

        perm_table = {
            'cyder_admin': ['all'],
            'admin': ['all'],
            'user': ['view', 'update'],
            'guest': ['view'],
        }

        # initialize obj into ctnrs
        obj = SOA()
        obj.primary = '192.168.1.1'
        obj.contact = '192.168.1.1'
        obj.save()
        domain = Domain(id=None, name='foo')
        domain.soa = obj
        domain.save()
        self.ctnr_admin.domains.add(domain)
        self.ctnr_user.domains.add(domain)
        self.ctnr_guest.domains.add(domain)
        self.save_all_ctnrs()

        self.check_perms_each_user(obj, perm_table)

    def test_domain_perms(self):
        """
        Test domain perms
        """
        self.setup_request()

        perm_table = {
            'cyder_admin': ['view', 'update'],
            'admin': ['view', 'update'],
            'user': ['view', 'update'],
            'guest': ['view'],
        }

        # initialize obj into ctnrs
        obj = Domain(id=None, name='foo')
        obj.save()
        self.ctnr_admin.domains.add(obj)
        self.ctnr_user.domains.add(obj)
        self.ctnr_guest.domains.add(obj)
        self.save_all_ctnrs()

        self.check_perms_each_user(obj, perm_table)

    def test_reverse_domain_perms(self):
        """
        Test reverse domain perms
        """
        self.setup_request()

        perm_table = {
            'cyder_admin': ['all'],
            'admin': ['all'],
            'user': ['all'],
            'guest': ['view'],
        }

        # initialize obj into ctnrs
        obj = ReverseDomain(id=None, name='128')
        obj.save()
        self.ctnr_admin.reverse_domains.add(obj)
        self.ctnr_user.reverse_domains.add(obj)
        self.ctnr_guest.reverse_domains.add(obj)
        self.save_all_ctnrs()

        self.check_perms_each_user(obj, perm_table)

    def test_domain_records_perms(self):
        """
        Test common domain record perms (cname, mx, txt, srv, ns)
        """
        self.setup_request()

        perm_table = {
            'cyder_admin': ['all'],
            'admin': ['all'],
            'user': ['all'],
            'guest': ['view'],
        }

        # initialize objs into ctnrs
        domain = Domain(id=None, name='foo')
        domain.save()
        self.ctnr_admin.domains.add(domain)
        self.ctnr_user.domains.add(domain)
        self.ctnr_guest.domains.add(domain)
        self.save_all_ctnrs()
        domain_records = []
        domain_records.append(AddressRecord(domain=domain))
        domain_records.append(CNAME(domain=domain))
        domain_records.append(MX(domain=domain))
        domain_records.append(SRV(domain=domain))
        domain_records.append(TXT(domain=domain))
        domain_records.append(Nameserver(domain=domain))

        for obj in domain_records:
            self.check_perms_each_user(obj, perm_table)

    def test_rdomain_records_perms(self):
        """
        Test common reverse domain record perms (ptr, reverse_ns)
        """
        self.setup_request()

        perm_table = {
            'cyder_admin': ['all'],
            'admin': ['all'],
            'user': ['all'],
            'guest': ['view'],
        }

        # initialize objs into ctnrs
        rdomain = ReverseDomain(id=None, name='128')
        rdomain.save()
        self.ctnr_admin.reverse_domains.add(rdomain)
        self.ctnr_user.reverse_domains.add(rdomain)
        self.ctnr_guest.reverse_domains.add(rdomain)
        self.save_all_ctnrs()
        rdomain_records = []
        rdomain_records.append(PTR(reverse_domain=rdomain))
        rdomain_records.append(ReverseNameserver(reverse_domain=rdomain))

        for obj in rdomain_records:
            self.check_perms_each_user(obj, perm_table)

    def setup_request(self):
        """
        Utility function for flushing and setting up request object for testing
        """
        self.request = HttpRequest()
        self.request.user = self.test_user
        self.request.session = SessionStore()

    def save_all_ctnrs(self):
        """
        Utility function that simply saves all of the defined ctnrs
        Called after adding an object to each one
        """
        self.ctnr_admin.save()
        self.ctnr_user.save()
        self.ctnr_guest.save()

    def check_perms_each_user(self, obj, perm_table):
        """
        Utility function for checking permissions
        """
        # superuser
        self.request.user = self.superuser
        self.request.session['ctnr'] = self.ctnr_guest
        self.assert_perms(obj, perm_table, 'superuser')

        # cyder admin
        self.request.user = self.cyder_admin
        self.request.session['ctnr'] = self.ctnr_guest
        self.assert_perms(obj, perm_table, 'cyder_admin')

        # admin
        self.request.user = self.test_user
        self.request.session['ctnr'] = self.ctnr_admin
        self.assert_perms(obj, perm_table, 'admin')

        # user
        self.request.session['ctnr'] = self.ctnr_user
        self.assert_perms(obj, perm_table, 'user')

        # guest
        self.request.session['ctnr'] = self.ctnr_guest
        self.assert_perms(obj, perm_table, 'guest')

        # pleb
        self.request.user = self.pleb_user
        self.assert_perms(obj, perm_table, 'pleb')

    def assert_perms(self, obj, perm_table, user_level):
        """
        Utility function that gets each type of permissions for an object and
        asserts against perm table.
        """
        create_perm = self.request.user.get_profile().has_perm(self.request, obj, 'create')
        view_perm = self.request.user.get_profile().has_perm(self.request, obj, 'view')
        update_perm = self.request.user.get_profile().has_perm(self.request, obj, 'update')
        delete_perm = self.request.user.get_profile().has_perm(self.request, obj, 'delete')

        perms = [create_perm, view_perm, update_perm, delete_perm]
        if user_level == 'superuser':
            for perm in perms:
                self.assertTrue(perm, "Superuser should full permissions.")
