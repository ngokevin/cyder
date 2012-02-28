
PTR Records
===========
PTR records are a simple DNS construct. They point an IP address to a name. They work the same in
IPv4 and IPv6.

PTRs in cyder
-------------
PTRs live in reverse zone files. They are 'pulled' out of the database as the reverse domain tree is
traversed.

Adding a PTR
++++++++++++
The internal interface for adding a PTR::

        def _add_generic_ptr( ip, name, domain, ip_type ):

``ip`` is a string and is either an IPv4 or IPv6 address. ``name`` and ``domain`` are a string and domain
instance. ``ip_type`` is either '4' or '6'. When you add a PTR record you should use either the
``add_ipv4_ptr`` or ``add_ipv6_ptr`` interface.::

        def add_ipv4_ptr( ip, fqdn )
            ...

        def add_ipv6_ptr( ip, fqdn )
            ...

What is important here is the ``fqdn`` parameter. cyder will attempt to match the fqdn to an
appropriate domain using a longest prefix match algorithm. Remember, for building purposes, the only
constraints on a PTR are the reverse domain and ip. The thing that the PTR is pointing to can be
anything.

Pointing to a fqdn that you aren't authoritative for
++++++++++++++++++++++++++++++++++++++++++++++++++++
What if you want to point an ip address that you are authoritative for (eg: ``128.193.1.1``) at a name
that you don't have an SOA for (eg: ``derp.com``)? This is how the PTR record would look in a Bind
zone file::

        1.1.193.128.in-addr.arpa.    PTR     derp.com

Let's also assume we don't have ``uberj.com`` or any ``.com`` domain names in the domain table. This
is how the PTR record would look in the in the database::

    id      name          IP    domain

    0       uberj.com     1     Null

Here the ``1`` in the IP column is a foreign key reference. cyder couldn't find a domain to tie this
record to, so it put the entire fqdn in the ``name`` column and set the domain to ``Null``. As another
example, let's say we are SOA for a domain (eg ``oregonstate.edu``) and want to point
and ip to a name within that domain (eg point ``128.193.1.1`` to ``foo.oregonstate.edu``). The database would have the following record::


    id      name                          IP    domain

    0       foo.oregonstate.edu           1     2

Here the ``2`` in the domain column is a foreign key to the ``oregonstate.edu`` domain. You might
also notice that name is still the fqdn. This is because there is no sain way to use ``$ORIGIN`` in
bind files for the data section of a PTR, so you will have to display the entire name anyway (this
differest to how names in A and AAAA records work).

Why?
++++
*Q*: Why go through all this extra effort to keep track of which domain the name in the PTR record points to?

*A*: Fast lookup will be possible with this scheme. When the interface is written you will be able
to go to a "domain" view and look at everything that is a domain. Any PTR records that point to a
name in your domain, even if not created by you, will show up. Of course, only users that have
access to the reverse domain will be able to edit these PTR's (PTR's point *IPs* to *names*).

TL;DR
+++++
The ``domain`` column is a nice feature to make data more relational, and it is not necissary.

PTR
---

.. automodule:: cyder.cydns.ptr.models
    :members:
