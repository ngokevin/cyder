from cyder.cybind.build import *
from django.core.management.base import BaseCommand, CommandError
from cyder.cydns.soa.models import SOA

class Command(BaseCommand):

    def handle(self, *args, **options):
        for soa in SOA.objects.all():
            print "### SOA file"
            print gen_soa(soa) # Eventually write to file
            domains_in_zone = soa.domain_set.all()
            for domain in domains_in_zone:
                print "+++ Domain file for %s" % (domain.name)
                print gen_domain(domain) # Eventually write to file

            print

