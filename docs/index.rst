Welcome to cyder's documentation!
=================================

    "It is highly recommended that you use some software which automates this checking, or generate your
    DNS data from a database which automatically creates consistent data."

    -- `RFC 1912 <http://tools.ietf.org/html/rfc1912>`_

`cyder <https://github.com/uberj/cyder>`_ is an `IPAM <http://en.wikipedia.org/wiki/IP_address_management>`_ solution. It is split up into two logically separate apps; ``cydns`` (DNS) and ``cydhcp`` (DHCP). The goal is two have the two apps be standalone and have less generic code 'glue' them together.

The 'glue' (not to be confused with DNS glue records) is found in ``core/``.

Maintain
--------
Cyder is designed to replace `Maintain <http://maintainproject.osuosl.org/>`_. Maintain 2.5 was the
last version released. Maintain 3 was written in purely in PHP and didn't work too well.
Aside from initially being written almost a decade ago, Maintain has been used in production at OSU
for over 10 years.

Taken from Maintain's README, here are the abridged requirements of Maintain:

* Web-based interface
* Ability to delegate authority of zone information to individual users/groups
* Quick updates (changes need to be reflected within 10 minutes)
* Advanced error reporting for zone transfers and DHCP server problems
* Generate zone files and DHCP configurations for primary and secondary DNS & DHCP servers
* Edit host information including MAC address, hostname, domain name, etc.
* Zone statistics such as total bandwidth used and bandwidth history for individual hosts
* Support for automatic registration on public networks (using authentication)
* Search by hostname, domain, zone, IP address and any other DNS type
* Ability to develop additional features through a module interface

Cyder will have all of these features and more.

Maintain Bugs
+++++++++++++
* DNSSEC is not supported.
* Top level DNS records were not supported (they have been hacked in).
* No support of other DNS output types. Only ``tinydns`` is supported.
* The following DNS record types are not supported ``SRV``, ``TXT``, (more)?
* DNS Zone delegation is broken.
* When a zone admin wants to manually assign an IP address to a client, DHCP needs to be bypassed.
  Maintian does this by providing a mac with all zeroes. It's a kludge.
* There can be several different ``defualt_domains`` assigned to the same range.
* Maintain was not built with a web framework. Ironically, this makes the code very hard to maintain.
* Written in PHP.

Maintain has it's weaknesses, but overall it does get the job done. It has already been shown that
Maintain's existing DNS scheme *does* `support building bind files
<https://github.com/uberj/maintain-bindbuilds>`_ (some modification to data in the database was
required due to poor data validation). Cyder is Maintain with a more formal structure. Cyder uses
many core concepts from Maintain.

.. toctree::
   :maxdepth: 2

   coding_standard
   validation
   ip
   domain
   reverse_domain
   common_record
   address_record
   ptr
   nameserver
   cname
   mx
   soa
   srv
   txt
   cybind

DNS
===
Vocabulary
----------
* Name and Label: "Each node in the DNS tree has a name consisting of zero or more labels"  `RFC4343 <http://tools.ietf.org/html/rfc4343>`_ . The name ``x.y.z`` consists of the labels ``x``, ``y``, and ``z``.

* Forward: Used to reference the part of DNS that maps names to Ip addresses.

* Reverse: Used to reverence the part of DNS that maps Ip addresses to names.

Domains and Reverse Domains
---------------------------
Domains and Reverse Domains are at the core of the DNS app. They are traversed during the build
process and will allow individual domain files to be built. This document goes over the design choices for domains and reverse domains. A solid understanding of DNS is assumed.


Domains
+++++++

A :ref:`domain` name in cyder a key part of the ordering of DNS records. Every domain name with
more than two labels has a ``master_domain`` that is not ``None``. A ``master_domain`` consists of the domain's name with the pre-fix label removed.

Consider ``foo.oregonstate.edu``. The labels ``foo``, ``oregonstate``, and ``edu`` all make up the
name ``foo.oregonstate.edu``. To calculate ``foo.oregonstate.edu``'s master domain, remove the
prefix-label, which in this case is ``foo``; ``oregonstate.edu`` is the master domain.

A ``domain`` with fewer than two labels it is permitted to have a master domain of ``None``. In all
other cases a domain *must* have a master domain. Cyder's django models enforce this.

This is the ``domain`` table's structure::

    +------------------+--------------+------+-----+---------+----------------+
    | Field            | Type         | Null | Key | Default | Extra          |
    +------------------+--------------+------+-----+---------+----------------+
    | id               | int(11)      | NO   | PRI | NULL    | auto_increment |
    | name             | varchar(100) | NO   | UNI | NULL    |                |
    | master_domain_id | int(11)      | YES  | MUL | NULL    |                |
    | soa_id           | int(11)      | YES  | MUL | NULL    |                |
    +------------------+--------------+------+-----+---------+----------------+

Note that ``master_domain_id`` is a foreign key that points back to the ``domain`` table. The
``soa_di`` field is a foreign key to the ``soa`` table.

Consider ``foo.oregonstate.edu`` and ``bar.oregonstate.edu``. The domain tree would look like the following::

    edu
    |
    oregonstate
    |       \
    foo     bar

The ``domain`` table in the database would have these records::

    id  name                    master_domain   SOA

    1   edu                     None            None
    2   oregonstate.edu         1               1 <--- the SOA table is not shown here
    3   foo.oregonstate.edu     2               1
    4   bar.oregonstate.edu     2               1

Note that the ``edu`` domain is in the table even though we are not authoritative for that domain.
It's ``SOA`` foreign key is set to ``None``.

You are not be able to add ``foo.oregonstate.edu`` without first adding ``oregonstate.edu``. Cyder
enforces that a full domain tree be maintained at all times.

Advantages of a Full Domain Tree
++++++++++++++++++++++++++++++++
Having a full tree makes things more complete. Also, when adding a new domain having a full tree removes any ambiguity when searching for a master domain.

Here are two examples of adding a domain. The first examples uses a partial domain tree. The second example uses a complete tree.

Using an Incomplete Tree
````````````````````````
Say we want to add ``cute.cat.com`` and assume we are *not* keeping a complete tree in the DB and that ``cute.cat.com`` is the first domain being added to the database (the ``domain`` table is empty). With an incomplete tree, ``cute.cat.com`` would have the master domain of ``None``::

    id  name                    master_domain   SOA

    1   cute.cat.com            None            1 <--- the SOA table is not show here

Let's now assume we are going to add ``cat.com``. At this point *if* we were using a full tree the ``com`` domain would be ``cute.com``'s master domain. The ``com`` domain is missing so ``cute.com``'s master domain is ``None``::

    id  name                    master_domain   SOA

    1   cute.cat.com            None            1
    2   cat.com                 None            1

After we add ``cat.com``, ``cute.cat.com``'s master domain is not correct. We need to search the
domain table to change ``cute.cat.com``'s master_domain to ``cat.com``'s ``id``, which is ``2``::

    id  name                    master_domain   SOA

    1   cute.cat.com            2               1
    2   cat.com                 None            1

Even when we didn't explicitly keep a complete tree, our data was converging towards completeness.
If we had added ``com`` we would have needed to update master domains and would be left with a full
tree.

Using a Full Tree Example
`````````````````````````
If we had to create all domains before we add a domain, adding the ``cute.cat.com`` domain would have resulted with the following records in the ``domain`` table::

    id  name                    master_domain   SOA

    1   com                     None            None
    2   cat.com                 1               None
    3   cute.cat.com            2               1

When we now add ``cat.com``, all we need to do is change the SOA field to signal that we are
authoritative for the domain::

    id  name                    master_domain   SOA

    1   com                     None            None
    2   cat.com                 1               1
    3   cute.cat.com            2               1

Reverse Domains
+++++++++++++++

The ``reverse_domain`` table stores the :ref:`reverse_domain` objects and has the following scheme::

    +--------------------------+--------------+------+-----+---------+----------------+
    | Field                    | Type         | Null | Key | Default | Extra          |
    +--------------------------+--------------+------+-----+---------+----------------+
    | id                       | int(11)      | NO   | PRI | NULL    | auto_increment |
    | name                     | varchar(100) | NO   | UNI | NULL    |                |
    | master_reverse_domain_id | int(11)      | YES  | MUL | NULL    |                |
    | soa_id                   | int(11)      | YES  | MUL | NULL    |                |
    | ip_type                  | varchar(1)   | NO   |     | NULL    |                |
    +--------------------------+--------------+------+-----+---------+----------------+

Here the ``master_reverse_domain_id`` field is a foreign key back to the ``reverse_domain`` table. The
``soa_id`` field is a foreign key to the ``soa`` table. The ``reverse_domain`` and ``domain`` tables
have very similar structure.

Consider the reverse domain ``20.193.128.in-addr.arpa``. In the data base it has the following
representation::

    128.193.20

The ``in-addr.arpa`` suffix is added during build time.

Here is the tree for the reverse domain ``128.193.20``::

    128
    |
    130
    |
    20

If we added the reverse domain ``21.193.128.in-addr.arpa``, the tree would look like this::

    128
    |
    130
    |  \
    20  21

The database would have the records::

    id  name        master_reverse_domain   SOA

    1   128         None                    None
    2   128.193     1                       1 <--- the SOA table is not shown here
    3   128.193.20  2                       1
    4   128.193.21  2                       1

The reverse domain ``128`` is in the database even though we do not have an SOA for it because ``193.128.in-addr.arpa`` can't be added without first adding ``128.in-addr.arpa``. The reasoning for keeping a complete tree are similar to the reasoning for forward domains.

Adding Reverse Domains
``````````````````````
Adding IPv4 reverse domains is easy to do by hand. It is not easy to do add IPv6 reverse domains by
hand. IPv6 reverse domain names are very long and it is tedious to add them one by one. There is a
function, :func:`bootstap_ipv6_reverse_domain`, that can aid in the construction of IPv6 reverse domains.

Reason For Reverse Domains
``````````````````````````
Reverse domains are used for DNS reverse mapping. In cyder, every IP is mapped to an appropriate
reverse domain. This mapping is explored in more detail in the Ip(link?) section of the documentation.

TLD's (Top Level Domains)
+++++++++++++++++++++++++
It is necisccary to have records (like :ref:`address_record`) that exist at the top level of a domain. Assume
we have two domains::

    oregonstate.edu
    foo.oregonstate.edu

Also, assume we are authoritative for both domains.

The ``domain`` table would have the following data::

    id  name                    master_domain   SOA
    1   edu                     None            None
    2   oregonstate.edu         1               1
    3   foo.oregonstate.edu     2               1

It is worth talking about where an A or AAAA record for ``foo.oregonstate.edu`` should exist. It
should exist in ``foo.oregonstate.edu`` and *not* in ``oregonstate.edu``. Cyder's django models
inforce this for most DNS records. If a CTNR admin has access to ``oregonstate.edu`` but does not have access to ``foo.oregonstate.edu`` it would not be correct for them to be able to create the record ``foo.oregonstate.edu  A  128.193.1.1`` in the ``oregonstate.edu`` domain. This would be a permissions leak.

No A or AAAA record can exist for a host if it is also a TLD. For our ``foo.oregonstate.edu`` domain, this is not allowed::

    (Record table)
    id  name    domain   ip
    1   foo     2        193.128.3.1

The correct entry is as follows::

    id  name    domain   ip
    1   ''      3        193.128.3.1

Here we use the empty string, ``''``, as the name for our record entry.

Changing from A to Domain
-------------------------

When an existing A or AAAA record becomes a domain (for example ``bar.oregonstate.edu`` is an A record, but then we decide to make the domain ``bar.oregonstate.edu``) the consistent thing to do would be to have cyder enforce that no A or AAAA records exist for a new domain. This means that an admin would have to delete the A or AAAA record for the new domain, make the new domain, and then create a TLD for the new domain.

Eventually, it might be nice to have a feature in the UI that does the migration from an A
or AAAA to a domain automatically. A nice `make this record into a domain` button.

SOA Records, Domains, and Zones
-------------------------------
An ``SOA`` record can only exist in one zone. It is critical that no two domains point to the same ``SOA`` record *and* be in different zones. See the :ref:`domain` documentation.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
