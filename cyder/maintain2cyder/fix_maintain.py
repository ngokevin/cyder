import ConfigParser
import MySQLdb
import pdb
config_file = "database.cfg"
config = ConfigParser.ConfigParser()
config.read(config_file)
connection = MySQLdb.connect(
                host=config.get( 'maintain_sb', 'host' ),
                user=config.get( 'maintain_sb', 'user' ),
                passwd=config.get( 'maintain_sb', 'passwd' ),
                db=config.get( 'maintain_sb', 'db' ))

cur = connection.cursor()
#cur.execute(""" SELECT * FROM `domain` WHERE `name`='foo.bar.baz' ;""" )
cur.execute(""" SELECT * FROM `domain` WHERE 1=1 ;""" )

broken_domains = cur.fetchall()
print "BROKEN DOMAINS========="
for domain in broken_domains:
    print domain[1]

needed_domains = set()

def find_or_insert_dname( dname ):
    search_sql =  "SELECT id FROM domain WHERE name='%s'" % (dname)
    cur.execute( search_sql )
    possible = cur.fetchone()
    if possible:
        return possible[0]

    sql =  "INSERT INTO domain (name, master_domain, enabled) VALUES('%s', %s, %s)" % (dname, 0, 1)
    status = cur.execute( sql )
    domain_id = cur.lastrowid
    connection.commit()
    return domain_id

def update_child( d_id, parent_id ):
    sql = "UPDATE domain SET master_domain=%s WHERE id=%s" % (parent_id, d_id)
    status = cur.execute( sql )
    connection.commit()
    if not status:
        pass

def update_master_domain( domain_id, parent_id ):
    sql = "UPDATE `domain` SET `master_domain`='%s' WHERE `id`='%s'" % (parent_id, domain_id)
    cur.execute( sql )
    connection.commit()
    return cur.lastrowid


def is_valid(dname):
    if dname.find('.') ==  -1:
        return True
    else:
        return False


def fix_domain( dname ):
    #pdb.set_trace()
    if is_valid(dname):
        # Base case
        domain_id = find_or_insert_dname( dname )
        return domain_id
    else:
        # Make sure I exist
        domain_id = find_or_insert_dname( dname )
        parent = '.'.join(dname.split('.')[1:])
        # Make sure my parent exists and is correct
        master_domain_id = fix_domain( parent )
        # Make sure I'm correct
        update_master_domain( domain_id, master_domain_id )
        # Return my id
        return domain_id



for domain in broken_domains:
    if domain[1].find('.in-addr.arpa') != -1:
        continue
    if domain[1] == '':
        continue
    if domain[1] == ' ':
        continue
    if domain[1] == '.':
        continue
    fix_domain( domain[1] )
    connection.commit()


print "CHANGED DOMAINS========="
for domain in needed_domains:
    print domain
