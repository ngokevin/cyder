.. _nameserver:

Nameservers
===========

Name server (NS) records are handled with some extra logic. "If the name server does lie within the
domain it should have a corresponding A record" -- `zytrax.com
<http://www.zytrax.com/books/dns/ch8/ns.html>`_. This corresponding A record is called a *glue
record*. Cyder will inforce the existance of glue records where they are needed. If you create an NS
record for a domain that you are authoritative for, you will be forced to create an glue record. For example:
You are authoritative for the ``foo.com`` domain and it's children domains and records (They are in
the ``foo.com`` zone). You go to create an NS entry for your nameserver ``ns1.foo.com``. You want
the record::

    foo.com     NS      ns1.foo.com


Before you add the NS entry, you need to create a glue record for ``ns1.foo.com``. The glue record
is just a ``A`` or ``AAAA`` record. Cyder will not allow the creation
of the NS entry before the glue record exists.

If you create an NS record that points to a name that exists outside of the domain you are making the
NS record for, you don't need to create the glue record. For example: You are authoritative for the
``foo.com`` zone in the exact same way you were for the previous example. You go to create an NS
record for the ``foo.com`` domain and you choose the name server ``ns1.bar.com``.  You want the
record::

        foo.com     NS      ns1.bar.com

You do not need to create a glue record.

Nameserver
----------
.. automodule:: cyder.cydns.nameserver.models
    :members:

