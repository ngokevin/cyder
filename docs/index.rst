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
        pass



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

Vocabulary
----------

Name and Label - "Each node in the DNS tree has a name consisting of zero or more labels" -- `RFC4343
<http://tools.ietf.org/html/rfc4343>`_ . The name ``x.y.z`` consists of the labels ``x``, ``y``, and
``z``.

Forward - Used to reference the part of DNS that maps names to Ip addresses.
Reverse - Used to reverence the part of DNS that maps Ip addresses to names.

Domains and Reverse Domains
---------------------------
Domains and Reverse Domains are at the core of the DNS app. They are traversed during the build
process and will allow individual zones files to be built. This document goes over the design choices for domains and reverse domains. A solid understanding of DNS is assumed.

Reverse Domains
+++++++++++++++

Consider the reverse domain ``20.193.128.in-addr.arpa``. It is stored as a ``VAR CHAR`` in the database and
is represented as::

    128.193.20

The ``in-addr.arpa`` suffix is added during build time.

Both Domains and Reverse Domains should be thought of as a tree data structure. Here is the tree for the reverse domain ``128.193.20``::

    128
    |
    130
    |
    20

If we added the reverse domain ``21.193.128.in-addr.arpa``, the tree would look like this.::

    128
    |
    130
    |  \
    20  21

The database would have the records.::

    id  name        master_reverse_domain   SOA

    1   128         None                    None
    2   128.193     1                       1 <--- the SOA table is not shown here
    3   128.193.20  2                       1
    4   128.193.21  2                       1

The reverse domain ``128`` is in the database even though we do not have an SOA for it. Keeping a
complete tree in the database allows adding new reverse domains to be an un-ambigous process. This means that you can't add ``193.128.in-addr.arpa`` without adding ``128.in-addr.arpa``.

Adding IPv4 reverse domains is easy to do by hand. It is not easy to do add IPv6 reverse domains by
hand. They are very long and it is tedious to add them one by one. There is a function,
``bootstap_ipv6_reverse_domain``, that can aid in the construction of reverse domains.

Reason For Reverse Domains
``````````````````````````
Reverse domains are used for DNS reverse mapping. In cyder, every IP is mapped to an appropriate
reverse domain. This mapping is explored in more detail in the Ip(link?) section of the documentation.

Domains
+++++++

Domains are very similar to reverse domains. They are stored recusivly where every domain name with
more than two labels has a ``master_domain``. A ``master_domain`` consists of the domain's name with the pre-fix label removed.

Consider ``foo.oregonstate.edu``. The labels ``foo``, ``oregonstate``, and ``edu`` all make up the
name ``foo.oregonstate.edu``. To calculate ``foo.oregonstate.edu``'s master domain, remove the
prefix-label, which in this case is ``foo``. The domain ``oregonstate.edu`` is the master domain.

When a ``domain`` has fewer than two labels it is permitted to have a master domain of ``None``. All
other times a domain *must* have a master domain. Cyders django models enforce this.

Consider ``foo.oregonstate.edu`` and ``bar.oregonstate.edu``. The domain tree would look like the following::

    edu
    |
    oregonstate
    |       \
    foo     bar

The database would have the records.::

    id  name                    master_domain   SOA

    1   edu                     None            None
    2   oregonstate.edu         1               1 <--- the SOA table is not shown here
    3   foo.oregonstate.edu     2               1
    4   bar.oregonstate.edu     2               1

Note the ``edu`` domain. It's in the database even though we are not SOA for that domain. And just as
it was with reverse domains, you are not be able to add ``foo.oregonstate.edu`` without first adding
``oregonstate.edu``. Fortunatly, boot strapping domains should not be an issue for forward Domains.

Why a full tree?
++++++++++++++++
It makes things more complete. It also removes any ambiguity when searching for a master domain when adding a new domain.

As an example, say we want to add ``cute.cat.com``. Assume we are *not* keeping a complete tree in the DB and this is the first domain being added to the database. It's master domain would be ``None``.::

    id  name                    master_domain   SOA

    1   cute.cat.com            None            1 <--- the SOA table is not show here

Let's now assume we are going to add ``cat.com``. At this point *if* we were using a full tree the ``com`` domain would be ``cute.com``'s master domain. For this example we are not using a full tree, so the ``com`` domain is missing and ``cute.com``'s master domain is ``None``.::

    id  name                    master_domain   SOA

    1   cute.cat.com            None            1
    2   cat.com                 None            1

``cute.cat.com``'s master domain is not correct. We need to search the domain table to change ``cute.cat.com``'s master_domain to cat.com's ``id``, which is ``2``.::

    id  name                    master_domain   SOA

    1   cute.cat.com            2               1
    2   cat.com                 None            1

Even when we didn't explicitly keep a complete tree, our data was converging towards completeness
(if we had added ``com`` we would have needed to update master domains and would be left with a full
tree).

If we had to create all domains before we add a domain and added ``cute.cat.com``, we would have the
following tree::

    id  name                    master_domain   SOA

    1   com                     None            None
    2   cat.com                 1               None
    3   cute.cat.com            2               1

When we now add ``cat.com``, all we need to do is change the SOA field.::

    id  name                    master_domain   SOA

    1   com                     None            None
    2   cat.com                 1               1
    3   cute.cat.com            2               1


TLD's (Top Level Domains)
+++++++++++++++++++++++++
It is necisccary to have records (like A records) that exist at the top level of a domain. Assume
we have two domains::

    oregonstate.edu
    foo.oregonstate.edu

The database, specifically the Domain table, would have the following data.::

    (Domain table)
    id  name                    master_domain   SOA
    1   edu                     None            None
    2   oregonstate.edu         1               1
    3   foo.oregonstate.edu     2               1

It is worth talking about where an A or AAAA record for ``foo.oregonstate.edu`` should exist. It
should exist in ``foo.oregonstate.edu`` and *not* in ``oregonstate.edu``. Cyders django models
inforce this for most DNS records. If a CTNR admin has access to ``oregonstate.edu`` but did not have access to ``foo.oregonstate.edu`` it would not be correct for them to be able to create the record ``foo.oregonstate.edu  A  128.193.1.1`` in the ``oregonstate.edu`` domain. This would be a permission leak.

No A or AAAA record can exist for a host if it is also a TLD. For our ``foo.oregonstate.edu`` domain, this is not allowed::

    (Record table)
    id  name    domain   ip
    1   foo     2        193.128.3.1

The correct entry is as follows.::

    id  name    domain   ip
    1   ''      3        193.128.3.1

Here we use the empty string, ``''``, as the name for our record entry.

When an existing A or AAAA record becomes a domain (for example ``bar.oregonstate.edu`` is an A record, but then we decide to make the domain ``bar.oregonstate.edu``) the consistent thing to do would be to have cyder enforce that no A or AAAA records exist for a new domain. This means that an admin would have to delete the A or AAAA record for the new domain, make the new domain, and then create a TLD for the new domain.

Eventually, it might be nice to have a feature in the UI that does the migration from an A
or AAAA to a domain automatically. A nice `make this record into a domain` button.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
