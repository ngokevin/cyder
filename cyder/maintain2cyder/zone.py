from utilities import long2ip
import pdb
import re
import printer
import sys
import os

from django.core.exceptions import ValidationError
from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.soa.models import SOA
from cyder.cydns.mx.models import MX
from cyder.cydns.cname.models import CNAME
from cyder.cydns.nameserver.models import Nameserver
"""
A Zone object should be initialized at a base domain. From that domain it should start to
build a zone file. These are the steps it shuold take to build it's zone file.
1) If there is an SOA, print it.
2) Print an $ORIGIN directive
3) Print Name Servers
4) Print MX records
5) Print A records
6) Print CNAMES
7) Get all domains that are `children` of that domain.
    7.a) For each child.
        * If there is an SOA for that child, make a new Zone object.
          Initialize that new zone with the new domain. Call walk_domain.
        * If the subdomain is part of this Zone (it has no new SOA),
          recurse starting at step 2.

PROBLEMS:
    MX records are being finiky. Example is kbvr.com.
        Notes kbvr: Search zone_mx for name= %skbvr%s
        It's domain is 543 which links to the com domain in the domain table.
    Solution: Add a record in the zone_mx table with name=''. The real problem is that
        records aren't allowed to live at the master domain level (they *can* be at subdomain
        level i.e. foo.oregonstate.edu can have an NS record, but oregonstate.edu can't. This
        is more of a bug in the maintain GUI than in the actual database.
"""
# Cyder Stuff
# We need to create some reverse domains for this script to work.
ips = []
# 127.0.0.0/24 I blame NOC
ips.append('127')
ips.append('131.252.80.131')
ips.append('207.98.68.5')

for ip in ips:
    split = ip.split('.')
    for i in range(len(split)):
        name = '.'.join(split[:i+1])
        ReverseDomain.objects.get_or_create( name = name, ip_type='4')





class Zone(object):
    BUILD_DIR="./build"
    SERIAL = 1
    DEFAULT_TTL = 999

    """
    @cur: database cursor
    @zone_fd: file descriptor to the db.* file (.*in-addr.arpa files are generated inside later)
    @domain: a maintain 'id' int corresponding to dname
    @dname: the actual string representation of the domain
                This helps bootstrap the process of generating revrse pointer .*in-addr.arpa files.

    """
    def __init__( self, cur, zone_fd, domain, dname ):
        self.cur = cur
        self.domain = domain
        self.dname = dname
        #self.printer = printer.Printer( fd=zone_fd )




    """
    The brians of the zone object.
    Notes: We skip domains with in-addr.arpa in their name (they are reverse domains).
        The Reverse_Zone object takes care of those specific domains.
    """
    def walk_domain( self, cur_domain , dname, parent_cdomain=None ):
        #TODO Consider moving the SOA genration into __init__
        soa = None
        if self.check_for_SOA( cur_domain, dname ):
            soa = self.gen_SOA( cur_domain, dname )

        new_domain = self.gen_domain( cur_domain, dname )
        if not new_domain:
            pdb.set_trace()
        # If we found an soa, assign it. Else inheirit soa from master (if master domain has one)
        if parent_cdomain:
            new_domain.soa = parent_cdomain.soa
            new_domain.save()

        self.cur.execute("""SELECT * FROM `domain` WHERE `name` NOT LIKE "%%.in-addr.arpa" AND `master_domain`=%s;""" % (cur_domain))
        domains = self.cur.fetchall()
        for subdomain in domains:
            child_name = subdomain[1]
            child_domain = subdomain[0]
            if self.check_for_SOA( child_domain, child_name ):
                zone_fd = None
                new_zone = Zone( self.cur, zone_fd, child_domain, child_name )
                new_zone.walk_domain( child_domain, child_name )
                continue
            self.walk_domain( child_domain, child_name, new_domain )

    def gen_domain( self, domain, dname ):
        self.cur.execute("SELECT * FROM `zone_mx` WHERE `domain`='%s' ORDER BY `name`;" % (domain))
        bad_dnames = ['', '.', '_']
        cdomain = None
        if dname not in bad_dnames:
            # Other baddies
            if dname.find('in-addr.arpa') >= 0:
                return None
            else:
                # IT's a good domain. First see if it exists already. Else create it.
                try:
                    cdomain, _ = Domain.objects.get_or_create( name = dname )
                except Exception, e:
                    print "ERROR: creating {0} {1}".format(dname, e)
                    return None
        if cdomain:
            print "Migrating %s (%s)" % (dname, cdomain.pk)

        #self.gen_MX( domain, dname, cdomain )
        self.gen_A( domain, dname, cdomain )
        #self.gen_dyn_ranges( domain, dname )
        #self.gen_CNAME( domain, dname, cdomain )
        self.gen_NS( domain, dname, cdomain )
        return cdomain

    def gen_MX( self, domain, dname, cdomain ):
        self.cur.execute("SELECT * FROM `zone_mx` WHERE `domain`='%s' ORDER BY `name`;" % (domain))
        records = self.cur.fetchall()
        self.gen_ORIGIN( domain, '' , Zone.DEFAULT_TTL )
        for record in records:
            name = record[1]
            domain = record[2]
            ttl = record[5]
            server = record[3]
            prio = record[4]
            ttl = record[5]
            # Cyder stuff
            if cdomain:
                try:
                    mx, _ = MX.objects.get_or_create( label=name, domain = cdomain, server = server, priority= prio, ttl = ttl )
                except ValidationError, e:
                    print "ERROR: %s. name: %s  cdomain: %s server: %s" %(str(e), name, str(cdomain), server)

        self.gen_ORIGIN( domain, dname , Zone.DEFAULT_TTL )

    """
    This function may be redundant.
    """
    def check_for_SOA( self, domain, dname ):
        self.cur.execute("SELECT * FROM `soa` WHERE `domain`='%s' ;" % (domain))
        records = self.cur.fetchall() # Could use fetch one. Want to do check though.
        if not records:
            # We don't have an SOA for this domain.
            return False
        else:
            return True

    def gen_SOA( self, domain, dname ):
        self.cur.execute("SELECT * FROM `soa` WHERE `domain`='%s' ;" % (domain))
        records = self.cur.fetchall() # Could use fetch one. Want to do check though.
        if not records:
            # We don't have an SOA for this domain.
            #self.printer.print_raw( ";No soa for "+dname+"  "+str(domain) )
            return
        record = records[0]
        primary_master = record[2]
        contact = record[3]
        REFRESH = record[4]
        RETRY = record[5]
        EXPIRE = record[6]
        MINIMUM = record[7] #TODO What is minimum, using TTL
        ##self.printer.print_SOA( record[7], dname, primary_master, contact, Zone.SERIAL, REFRESH, RETRY, EXPIRE, MINIMUM )
        # Let's create an soa in the new database and return it.
        try:
            soa, _ = SOA.objects.get_or_create( primary =
                    primary_master, contact = contact, comment="SOA for "
                    "{0} zone".format(dname))
        except:
            print "ERROR: creating soa {0}".format(soa)
        return soa


    def gen_ORIGIN( self, domain, dname, ttl ):
        origin = "$ORIGIN  %s.\n" % (dname)
        origin += "$TTL     %s\n" % (ttl)
        ##self.printer.print_raw( origin )

    def gen_CNAME( self, domain, dname, cdomain ):
        self.cur.execute("SELECT * FROM `zone_cname` WHERE `domain`='%s';" % (domain))
        records = self.cur.fetchall()
        for record in records:
<<<<<<< HEAD
            ##self.printer.print_CNAME( record[2], record[1] )
=======
            self.printer.print_CNAME( record[2], record[1] )
>>>>>>> de9599ab6787125afba08c52ddf4e6c983ad413d
            try:
                cname, created = CNAME.objects.get_or_create( label=record[2], domain=cdomain, data=record[1])
            except:
                print "ERROR creating cname: {0} {1}".format(record[2],
                        record[1])

    def gen_dyn_ranges( self, domain, dname ):
        ##self.printer.print_raw( "; Gen dyn_ranges for %s\n" % (dname) )
        self.cur.execute(  "SELECT start, end FROM ranges, zone_range\
                            WHERE ranges.id = zone_range.range AND zone_range.default_domain = %s\
                            AND ranges.type='dynamic' ORDER by start" % (domain) )
        ip_ranges = self.cur.fetchall()
        for ip_range in ip_ranges:
            for ip in range(ip_range[0],ip_range[1]+1):
                ip = long2ip(ip)
                ##self.printer.print_A( ip.replace('.','-'),ip )
    """
    domain: maintain id of the domain
    dname: the base name of that domain. i.e. domain 218 has dname oregonstate.edu
    """

    def gen_A( self, domain, dname, cdomain ):
        self.gen_host( domain, dname, cdomain )
        #self.gen_forward_pointers( domain, dname, cdomain )

    """
    Generate all A records from the pointer table (forward pointers)
    This function should grab every forward table from the (broken) pointer table.
    if pointer == <some domain>:
        create a TLD A record
    else:
        strip label
        find domain
        create A record in domain using label
    """
    def gen_forward_pointers(self):
        sql = "SELECT * FROM `pointer` WHERE `type`='forward' ORDER BY hostname"
        self.cur.execute(sql)
        records = self.cur.fetchall()
        # We have abosulte names in the pointer table so print a root origin.
        for record in records:
            # Start Cyder
            domain = Domain.objects.filter( name = record[2] ) #This is a TLD record
            if domain:
                name = ''
                cdomain = domain[0]
            else:
                name = record[2].split('.')[0] # Get the front label
                dname = '.'.join(record[2].split('.')[1:])
                cdomain = Domain.objects.filter( name = dname )
                if not cdomain:
                    split = dname.split('.')
                    for i in list(reversed(range(len(split)))):
                        name = '.'.join(split[i:])
                        cdomain, created = Domain.objects.get_or_create( name = name )
                        cdomain.save()
                else:
                    cdomain = cdomain[0]

            ip_str = long2ip(record[1])
            try:
                AddressRecord.objects.get_or_create( label=name,
                        domain= cdomain, ip_str=ip_str, ip_type='4' )
            except ValidationError, e:
                print "ERROR: %s name: %s domain: %s ip: %s" % (str(e), name, cdomain.name, ip_str )

        # Revert to dname origin.
        self.gen_ORIGIN( domain, dname , 999 )

    """
    Generate all A records from the host table.
    """
    def gen_host( self, domain, dname, cdomain ):
        self.cur.execute("SELECT * FROM `host` WHERE `domain`='%s';" % (domain))
        records = self.cur.fetchall()
        for record in records:
            if record[1] == 0:
                continue
<<<<<<< HEAD
            #self.printer.print_A( record[3] , long2ip(record[1]) )
            name= record[3]
            ip_str = long2ip(record[1])
            arec, _ = AddressRecord.objects.get_or_create( label=name,
                    domain= cdomain, ip_str=ip_str, ip_type='4' )
=======
            self.printer.print_A( record[3] , long2ip(record[1]) )
            name= record[3]
            ip_str = long2ip(record[1])
            print "{0} A {1}".format(name, ip_str)
            try:
                AddressRecord.objects.get_or_create( label=name,
                        domain= cdomain, ip_str=ip_str, ip_type='4' )
            except ValidationError, e:
                print "ERROR: %s name: %s domain: %s ip: %s" % (str(e), name, cdomain.name, ip_str )
>>>>>>> de9599ab6787125afba08c52ddf4e6c983ad413d

    def gen_NS( self, domain, dname, cdomain=None ):
        self.cur.execute("SELECT * FROM `nameserver` WHERE `domain`='%s';" % (domain))
        records = self.cur.fetchall()
        #self.printer.print_NS( '', [ record[1] for record in records ] )
        # TODO we need glue records for some of these.
        if cdomain:
            for record in records:
                ns_name = record[1]
                possible = Nameserver.objects.filter( domain = cdomain, server = ns_name )
                if possible:
                    continue
                try:
                    ns, _ = Nameserver.objects.get_or_create( domain = cdomain, server = ns_name )
<<<<<<< HEAD
                except Exception, e:
                    print "ERROR: couldn't create ns {0} {1}".format(ns_name, e)
=======
                except:
                    print "ERROR: couldn't create ns {0}".format(ns_name)
>>>>>>> de9599ab6787125afba08c52ddf4e6c983ad413d
