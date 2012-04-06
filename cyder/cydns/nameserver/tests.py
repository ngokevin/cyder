from django.test import TestCase
from django.test.client import Client

from django.core.exceptions import ValidationError

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
