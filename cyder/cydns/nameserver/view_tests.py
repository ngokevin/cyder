from django.test import TestCase
from django.test.client import Client

from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.tests.view_tests import GenericViewTests, random_label
from cyder.settings import CYDNS_BASE_URL
