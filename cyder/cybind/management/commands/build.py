from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.soa.models import SOA
from cyder.cydns.ip.models import Ip
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.nameserver.models import Nameserver
from cyder.cybind.build import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        print gen_soa(s)
        print gen_domain(d1)

