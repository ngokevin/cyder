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
        self.test_user = User.objects.get_or_create(username='test_user', password='test_user')[0]

        self.setup_request()

        # superuser
        self.super_user = User.objects.get(username='development')

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

    def test_session_has_ctnr_dev(self):
        """
        Test middleware sets session ctnr on log in
        Precondition: no session container
        Postcondition: session container
        """
        self.setup_request()
        self.request.user = AnonymousUser()

        dev_middleware = DevAuthenticationMiddleware()
        dev_middleware.process_request(self.request)

        self.assertTrue('ctnr' in self.request.session)

    def test_ctnr_domain(self):
        """
        Test being in ctnr /w domain gives appropriate perms
        Precondition: domain in ctnr
        Postcondition: has full perm to domain if admin, read only if not
        """
        self.setup_request()

        # initialize obj into ctnrs
        obj = Domain(id=None, name='foo')
        obj.save()
        self.ctnr_admin.domains.add(obj)
        self.ctnr_user.domains.add(obj)
        self.ctnr_guest.domains.add(obj)
        self.save_all_ctnrs()

        self.check_perms(obj)

    def test_ctnr_reverse_domain(self):
        """
        Test being in ctnr /w rdomain gives appropriate perms
        Precondition: rdomain in ctnr
        Postcondition: full perm if admin, read only if not
        """
        self.setup_request()

        # initialize obj into ctnrs
        obj = ReverseDomain(id=None, name='128')
        obj.save()
        self.ctnr_admin.reverse_domains.add(obj)
        self.ctnr_user.reverse_domains.add(obj)
        self.ctnr_guest.reverse_domains.add(obj)
        self.save_all_ctnrs()

        self.check_perms(obj)

    def test_ctnr_domain_records(self):
        """
        Test being in ctnr /w common domain records gives appropriate perms
        common domain records: cname, mx, txt, srv
        """
        self.setup_request()

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
        domain_records.append(Nameserver(domain=domain))
        domain_records.append(SRV(domain=domain))
        domain_records.append(TXT(domain=domain))

        for obj in domain_records:
            self.check_perms(obj)

    def test_ctnr_rdomain_records(self):
        """
        Test being in ctnr /w common domain records gives appropriate perms
        common domain records: cname, mx, txt, srv
        """
        self.setup_request()

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
            self.check_perms(obj)

    def test_ctnr_soa(self):
        """
        Test being in ctnr /w soa record gives appropriate perms
        """
        self.setup_request()

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

        self.check_perms(obj)

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

    def check_perms(self, obj):
        """
        Utility function for checking permissions
        """
        # admin
        self.request.session['ctnr'] = self.ctnr_admin
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'create')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'view')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'update')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'delete')

        # user
        self.request.session['ctnr'] = self.ctnr_user
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'create')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'view')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'update')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'delete')

        # guest
        self.request.session['ctnr'] = self.ctnr_guest
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'create')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'view')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'update')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'delete')

        # pleb
        self.request.user = self.pleb_user
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'create')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'view')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'update')
        has_perm = self.test_user.get_profile().has_perm(self.request, obj, 'delete')
