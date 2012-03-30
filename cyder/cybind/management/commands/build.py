from cyder.cybind.build import *
from django.core.management.base import BaseCommand, CommandError
from cyder.cydns.soa.models import SOA

class Command(BaseCommand):

    def handle(self, *args, **options):
        build_dns(*args, **options)
