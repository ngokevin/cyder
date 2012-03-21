from utilities import long2ip
import pdb
import re
import printer
import sys
import os

from cyder.cydns.cydns import InvalidRecordNameError
from cyder.cydns.domain.models import Domain, DomainExistsError
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import Ip
from cyder.cydns.soa.models import SOA
from cyder.cydns.mx.models import MX
from cyder.cydns.cname.models import CNAME
from cyder.cydns.nameserver.models import Nameserver, _needs_glue
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
        self.printer = printer.Printer( fd=zone_fd )




    """
    The brians of the zone object.
    Notes: We skip domains with in-addr.arpa in their name (they are reverse domains).
        The Reverse_Zone object takes care of those specific domains.
    """
    def walk_domain( self, cur_domain , dname ):
        #TODO Consider moving the SOA genration into __init__
        soa = None
        if self.check_for_SOA( cur_domain, dname ):
            soa = self.gen_SOA( cur_domain, dname )

        new_domain = self.gen_domain( cur_domain, dname )
        # If we found an soa, assign it. Else inheirit soa from master (if master domain has one)
        if soa and new_domain:
            new_domain.soa = soa
            new_domain.save()
        else:
            if new_domain and new_domain.master_domain and new_domain.master_domain.soa:
                new_domain.soa = new_domain.master_domain.soa
                new_domain.save()

        self.cur.execute("""SELECT * FROM `domain` WHERE `name` NOT LIKE "%%.in-addr.arpa" AND `master_domain`=%s;""" % (cur_domain))
        domains = self.cur.fetchall()
        for subdomain in domains:
            child_name = subdomain[1]
            child_domain = subdomain[0]
            if self.check_for_SOA( child_domain, child_name ):
                zone_fd = open( "%s/%s" % (Zone.BUILD_DIR, child_name), "w+")
                new_zone = Zone( self.cur, zone_fd, child_domain, child_name )
                new_zone.walk_domain( child_domain, child_name )
                continue
            self.walk_domain( child_domain, child_name )

    def gen_domain( self, domain, dname ):
        print "Generating %s" % (dname)
        self.gen_ORIGIN( domain, dname, 999 )
        bad_dnames = ['', '.', '_']
        cdomain = None
        if dname not in bad_dnames:
            # Other baddies
            if dname.find('in-addr.arpa') >= 0:
                pass
            else:
                # IT's a good domain. First see if it exists already. Else create it.
                possible = Domain.objects.filter( name = dname )
                if possible:
                    cdomain = possible[0]
                else:
                    cdomain = Domain( name = dname )
                    try:
                        cdomain.save()
                    except DomainExistsError, e:
                        print "ERROR: %s " % dname
                        pass

        self.gen_MX( domain, dname, cdomain )
        self.gen_A( domain, dname, cdomain )
        self.gen_dyn_ranges( domain, dname )
        self.gen_CNAME( domain, dname, cdomain )
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
            if name == "":
                self.printer.print_MX( dname, domain, ttl, prio, server  )
            else:
                self.printer.print_MX( name+"."+dname, domain, ttl, prio, server  )
            # Cyder stuff
            if cdomain:
                possible = MX.objects.filter( label=name, domain = cdomain, server = server, priority= prio, ttl = ttl )
                if possible: # Have we already created this?
                    pass
                else: # Create a new mx
                    print name
                    print server
                    print cdomain
                    mx = MX( label=name, domain = cdomain, server = server, priority= prio, ttl = ttl )
                    try:
                        mx.save()
                    except InvalidRecordNameError, e:
                        print "ERROR: %s. name: %s  cdomain: %s server: %s" %(str(e), name, str(cdomain), server)

        self.gen_ORIGIN( domain, dname , Zone.DEFAULT_TTL )

    """
    This function may be redundant.
    """
    def check_for_SOA( self, domain, dname ):
        self.cur.execute("SELECT * FROM `soa` WHERE `domain`='%s' ;" % (domain))
        records = self.cur.fetchall() # Could use fetch one. Want to do check though.
        if len(records) > 1:
            self.printer.print_raw( ";Sanity Check failed\n" )
        if not records:
            # We don't have an SOA for this domain.
            return False
        else:
            return True

    def gen_SOA( self, domain, dname ):
        self.cur.execute("SELECT * FROM `soa` WHERE `domain`='%s' ;" % (domain))
        records = self.cur.fetchall() # Could use fetch one. Want to do check though.
        if len(records) > 1:
            self.printer.print_raw( ";Sanity Check failed" )
        if not records:
            # We don't have an SOA for this domain.
            self.printer.print_raw( ";No soa for "+dname+"  "+str(domain) )
            return
        record = records[0]
        primary_master = record[2]
        contact = record[3]
        REFRESH = record[4]
        RETRY = record[5]
        EXPIRE = record[6]
        MINIMUM = record[7] #TODO What is minimum, using TTL
        self.printer.print_SOA( record[7], dname, primary_master, contact, Zone.SERIAL, REFRESH, RETRY, EXPIRE, MINIMUM )
        # Let's create an soa in the new database and return it.
        possible = SOA.objects.filter( primary = primary_master, contact = contact )
        if possible:
            return possible[0]
        soa = SOA( primary = primary_master, contact = contact, retry = RETRY, refresh = REFRESH )
        soa.save()
        return soa


    def gen_ORIGIN( self, domain, dname, ttl ):
        origin = "$ORIGIN  %s.\n" % (dname)
        origin += "$TTL     %s\n" % (ttl)
        self.printer.print_raw( origin )

    def gen_CNAME( self, domain, dname, cdomain ):
        self.cur.execute("SELECT * FROM `zone_cname` WHERE `domain`='%s';" % (domain))
        records = self.cur.fetchall()
        for record in records:
            self.printer.print_CNAME( record[2], record[1] )
            cname, created = CNAME.objects.get_or_create( label=record[2], domain=cdomain, data=record[1])
            cname.save()

    def gen_dyn_ranges( self, domain, dname ):
        self.printer.print_raw( "; Gen dyn_ranges for %s\n" % (dname) )
        self.cur.execute(  "SELECT start, end FROM ranges, zone_range\
                            WHERE ranges.id = zone_range.range AND zone_range.default_domain = %s\
                            AND ranges.type='dynamic' ORDER by start" % (domain) )
        ip_ranges = self.cur.fetchall()
        for ip_range in ip_ranges:
            for ip in range(ip_range[0],ip_range[1]+1):
                ip = long2ip(ip)
                self.printer.print_A( ip.replace('.','-'),ip )
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
            if not AddressRecord.objects.filter( label = name, domain= cdomain, ip__ip_str = ip_str ):
                ip = Ip( ip_str= ip_str, ip_type='4')
                ip.save()
                rec = AddressRecord( label=name, domain = cdomain, ip = ip , ip_type='4' )
                try:
                    rec.save()
                except InvalidRecordNameError, e:
                    print "ERROR: %s name: %s domain: %s ip: %s" % (str(e), name, cdomain.name, ip_str )
                    ip.delete()
            else:
                print "SKIPPING name: %s domain: %s ip: %s (already created)" % (name, cdomain.name, ip_str )

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
            self.printer.print_A( record[3] , long2ip(record[1]) )
            print record[3]
            print long2ip(record[1])
            if not AddressRecord.objects.filter( label = record[3], domain= cdomain, ip__ip_str = long2ip(record[1]) ):
                ip = Ip( ip_str=long2ip(record[1]), ip_type='4')
                ip.save()
                rec = AddressRecord( label=record[3], domain = cdomain, ip =ip , ip_type='4' )
                try:
                    rec.save()
                except InvalidRecordNameError, e:
                    print "ERROR: %s name: %s domain: %s ip: %s" % (str(e), record[3], cdomain.name, long2ip(record[1]))
                    ip.delete()
            else:
                print "SKIPPING %s %s %s (already created)" % (record[3], cdomain.name, long2ip(record[1]))

    def gen_NS( self, domain, dname, cdomain=None ):
        self.cur.execute("SELECT * FROM `nameserver` WHERE `domain`='%s';" % (domain))
        records = self.cur.fetchall()
        self.printer.print_NS( '', [ record[1] for record in records ] )
        # TODO we need glue records for some of these.
        if cdomain:
            for record in records:
                ns_name = record[1]
                possible = Nameserver.objects.filter( domain = cdomain, server = ns_name )
                if possible:
                    print "SKIPPING: nameserver: %s domain: %s (already created)" % (ns_name, cdomain.name)
                    continue
                ns = Nameserver( domain = cdomain, server = ns_name )
                if _needs_glue(ns):
                    a_rec = AddressRecord.objects.filter( label = ns_name.split('.')[0], domain=cdomain )
                    if not a_rec:
                        print "ERROR: Could not find glue. ns: %s domain: %s" % (ns_name, cdomain.name)
                        continue
                    else:
                        a_rec = a_rec[0]
                    ns.glue = a_rec
                try:
                    ns.save()
                except InvalidRecordNameError, e:
                    print "ERROR: %s nameserver: %s domain: %s" % (str(e), ns_name, cdomain.name)
