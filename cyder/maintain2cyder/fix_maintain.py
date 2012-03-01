from database import Database
import pdb
db = Database()
db.config_file = "database.cfg"
db.retry()
cur = db.get_cursor("maintain_sb")

cur.execute(""" SELECT id, name
                FROM `domain`
                WHERE `name`
                LIKE "%%.%"
                AND `master_domain`=0;""" )

broken_domains = cur.fetchall()

needed_domains = set()

def insert_dname( parent ):
    sql =  "INSERT INTO domain (name, master_domain, enabled) VALUES ('%s', %s, %s)" % (parent, 0, 1)
    search_sql =  "SELECT id FROM domain WHERE name='%s'" % (parent)
    status = cur.execute( sql )
    possible_id = cur.fetchone()
    status = cur.execute( sql )
    if not status:
        print "ERROR: %s" % (parent)
    parent_id = cur.lastrowid
    return parent_id

def update_child( d_id, parent_id ):
    sql = "UPDATE domain SET master_domain=%s WHERE id=%s" % (parent_id, d_id)
    status = cur.execute( sql )
    if not status:
        pass



def fix_domain( dname, d_id ):
    parent = '.'.join(dname.split('.')[1:])
    if parent == 'orvsd.org':
        pdb.set_trace()
    needed_domains.add( parent )
    if is_valid(parent):
        parent_id = insert_dname( parent )
        return parent_id
    else:
        parent_id = fix_domain( parent, d_id )
        update_child( d_id, parent_id )
        return parent_id

def is_valid(dname):
    if dname.find('.') ==  -1:
        return True
    else:
        return False

for domain in broken_domains:
    if domain[1].find('.in-addr.arpa') != -1:
        continue
    if domain[1] == '':
        continue
    if domain[1] == '.':
        continue
    parent_id = fix_domain( domain[1], domain[0] )
    update_child( domain[0], parent_id )


for domain in needed_domains:
    print domain
