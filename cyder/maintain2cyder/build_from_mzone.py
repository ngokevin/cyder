from utilities import long2ip
import pdb
import re
import printer
import sys
import os

from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.soa.models import SOA
from cyder.cydns.mx.models import MX
from cyder.cydns.cname.models import CNAME

class MZone(object):

    def __init__(self, cur):
        self.cur = cur

    def get_all_zones(self):
        self.cur.execute("""SELECT id, name FROM zone;""")
        zones = self.cur.fetchall()
        return zones

    def migrate(self):
        for zone in self.get_all_zones():
            print "{0} ({1})".format(zone[1], zone[0])
        return

