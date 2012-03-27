from cyder.cybind.build import *
from django.core.management.base import BaseCommand, CommandError
from cyder.cydns.domain.models import Domain

class Command(BaseCommand):

    def handle(self, *args, **options):
        d1 = Domain.objects.filter(name='foo.gaz')[0] # temporary hack for testing purposes
        s = d1.soa
        print "################## SOA file ###################"
        print gen_soa(s)
        print "############# Domain file for %s ##############" % (d1.name)
        print gen_domain(d1)

