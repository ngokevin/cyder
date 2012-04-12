.. _domain:

Domain
======

Delegating a subdomain
----------------------

When a domain is delegated the interface with which a CTNR admin creates
new objects changes. Instead of being able to create all DNS record
types, they can only create NS records and glue records.

The UI should only have a link to the create address record form and a
form that creates an NS record and an A record in one submit.

Domain
------
.. automodule:: cyder.cydns.domain.models
    :members:
