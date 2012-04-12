.. _dns_views:

DNS Views
---------
It is highly likely that some records should be viewable from inside OSU and
not visable from outside OSU. Do do this we will need to use bind DNS views.

The nameserver conf file::

    view "internal-view" {
      match-clients { 128.193.0.0/16; 10.0.0.0/8 };
      zone "foo.com" IN {
        type master;
        file "zones/db.foo.com.internal";
     };
    };

    view "external-view" {
      match-clients { any; };
      zone "foo.com" IN {
        type master;
        file "zones/db.foo.com.external";
      };
    };

The files::

    FILE: db.foo.com.soa
    @   1D  IN  SOA ns1.foo.com hostmaster.foo.com (
                    1;
                    2;
                    3;
                    4;
                    5;
                )

    FILE: db.foo.com.data.external

    @       IN  NS  ns1.foo.com
    @       MX  10  mail.foo.com
    ns1     A   128.193.1.4
    mail    A   128.193.1.5

    FILE: db.foo.com.data.internal

    bob     A   10.0.0.2
    mary    A   10.0.0.3

The external zone file::

    FILE: db.foo.com.external

    $INCLUDE db.foo.com.soa
    $INCLUDE db.foo.com.external

The internal zone file::

    FILE: db.foo.com.internal

    $INCLUDE db.foo.com.soa
    $INCLUDE db.foo.com.data.external
    $INCLUDE db.foo.com.data.internal

Questions right now:

 * How should we decide which records go into the external and internal files?
 * What if we want more views?
