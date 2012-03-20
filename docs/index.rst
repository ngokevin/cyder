.. cyder documentation master file, created by
   sphinx-quickstart on Tue Jan 10 15:54:05 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to cyder's documentation!
=================================

cyder is an `IPAM <http://en.wikipedia.org/wiki/IP_address_management>`_ system. It is split up into two logically separate apps; ``cydns`` (DNS) and ``cydhcp`` (DHCP). The goal is two have the two apps be standalone and have less generic code 'glue' them together.

The 'glue' (not to be confused with DNS glue records) is found in ``core/``.

Coding Ideas (Standards)
------------------------

No trailing white space anywhere.

Parentheses should have no spaces next to them::

    def good_function(self):
        pass

    def bad_function( self ):



Model code should have 100% statement coverage.

Before you do anything with an IP address (as a string or int) put it into the ipaddr library
functions IPv4Address and IPv6Address. This will standardize how things are formated, stored, and
displayed.

DNS
===
Modules related to the DNS app.

.. toctree::
   :maxdepth: 2

   ip
   domain
   reverse_domain
   address_record
   ptr
   nameserver
   cname
   mx
   soa
   srv
   txt

Domains and Reverse Domains
---------------------------
Domains and Reverse Domains are at the core of the DNS app. They are traversed during the build
process and will allow individual zones files to be built. There are some core ideas that are
helpful to understand about how these two objects are implemented. A solid understanding of DNS is
assumed.

Reverse Domains
+++++++++++++++

Consider the reverse domain 20.193.128.in-addr.arpa. It is stored as a VAR CHAR in the database and
is represented as::

    128.193.20

(The in-addr.arpa cruft is only added during build time).

Both Domains and Reverse Domains should be thought of as a tree data structure. So for our example,::

    128
    |
    130
    |
    20

If we added 21.193.128.in-addr.arpa it would look like.::

    128
    |
    130
    |  \
    20  21

The database would have the records.::

    id  name        master_reverse_domain   SOA

    1   128         Null                    Null
    2   128.193     1                       1 <--- the SOA table is not shown here
    3   128.193.20  2                       1
    4   128.193.21  2                       1

The reverse domain ``128`` is in the database even though we do not have an SOA for it. Keeping a
complete tree in the database is (in my mind) a good idea. It also allows adding new reverse domains
an un-ambigous process. But what does this mean? You can't add ``193.128.in-addr.arpa`` without adding
``128.in-addr.arpa``. This is find for Ipv4 reverse domains, but what about Ipv6 reverse domains? They
are very long and it would be tedious to add them one by one. TODO there should be a function in
``cydns/reverse_domain/models.py`` that aids in the bootstrapping process of creating Ipv6 reverse
domains.

Domains
+++++++

Domains are very similar to reverse domains. Consider foo.bar.oregonstate.edu. The tree would look
like::

    edu
    |
    oregonstate
    |       \
    foo     bar

The database would have the records.::

    id  name                    master_domain   SOA

    1   edu                     Null            Null
    2   oregonstate.edu         1               1 <--- the SOA table is not shown here
    3   foo.oregonstate.edu     2               1
    4   bar.oregonstate.edu     2               1

Note the ``edu`` domain. It's in the database even though we are not SOA for that domain. And just as
it was with reverse domains, you should not be able to add foo.oregonstate.edu without adding
oregonstate.edu first. Fortunatly, boot strapping domains should not be an issue for plain Domains.

Why a full tree?
++++++++++++++++
I for see the question "Why do you have the edu domain in the database? You aren't authoritative for
that domain!". I also asked myself that question, and the answer I came up with is "It makes things
more complete". It also removes any ambiguity when searching for a master domain for a new domain
being added. Here is an example.

Say we want to add cute.cat.com. Let's say we are *not* keeping a complete tree in the DB and this
is the first domain we added. It's master domain would be ``Null``.::

    id  name                    master_domain   SOA

    1   cute.cat.com            Null            1 <--- the SOA table is not show here

Let's now assume we are going to add cat.com. We don't have a ``com`` domain, so it's master domain is
``Null``.::

    id  name                    master_domain   SOA

    1   cute.cat.com            Null            1
    2   cat.com                 Null            1

This obviously isn't correct. We need to search the domain table to change cute.cat.com's
master_domain to 2, cat.com's ``id``.::

    id  name                    master_domain   SOA

    1   cute.cat.com            2               1
    2   cat.com                 Null            1

We still have to keep the tree complete. Now consider if we had to create all domains before we add a
domain. When we add cute.cat.com::

    id  name                    master_domain   SOA

    1   com                     Null            Null
    2   cat.com                 1               Null
    3   cute.cat.com            2               1

When we acquire cat.com, all we need to do is change the SOA field!::

    id  name                    master_domain   SOA

    1   com                     Null            Null
    2   cat.com                 1               1
    3   cute.cat.com            2               1

That's my attempt to justify.

TLD's (Top Level Domains)
+++++++++++++++++++++++++
How should we handle TDL's. Specifically, how should we handle A records that point to a TLD. Let's
assume we have two domains::

    oregonstate.edu
    foo.oregonstate.edu

The database, specifically the Domain table, would look like::

    (Domain table)
    id  name                    master_domain   SOA
    1   edu                     Null            Null
    2   oregonstate.edu         1               1
    3   foo.oregonstate.edu     2               1

The issue is where an A or AAAA record for ``foo.oregonstate.edu`` should exist. Should it exist in
``oregonstate.edu`` or in ``foo.oregonstate.edu``? We definitely do not want it to exist in both domains. That would be confusing. What if a CTNR admin knew about the one in ``foo.oregonstate.edu`` but not the one in ``oregonstate.edu``. It would be confusing if they saw two different IP's for it when they queried the name server.

No A or AAAA record can exist for a host if it is also a TLD. For our ``foo.oregonstate.edu`` domain, this is not allowed::

    (Record table)
    id  name    domain   ip
    1   foo     2        193.128.3.1

A correct entry would be::

    id  name    domain   ip
    1   ''      3        193.128.3.1

Here we use the empty string, ``''``, as the name for our record entry.

But what happens when an existing A or AAAA record becomes a domain (for example ``bar.oregonstate.edu`` is an A record, but then we decide to make the domain ``bar.oregonstate.edu``)? The consistent thing to do would be to have cyder enforce that no A or AAAA records exist for a new domain. So in our case we would have to delete the A or AAAA record for the new domain, make the new domain, and then create a TLD for the new domain.

Eventually, it might be nice to have a feature in the UI that does the migration from an A
or AAAA to a domain automatically. A nice `make this record into a domain` button.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
