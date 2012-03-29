.. _domain:

Domains
=======

Delegating a subdomain
----------------------
To delegate a domain in cyder, create an :ref:`nameserver` record that points to the nameservers that you are delegating the subdomain to, add the appropriate A and AAAA glue records, and finally mark a domain as "delegated".

When a domain is marked as "delegated" in the database, no new records can be added to that domain. Editing existing records is still possible. Editing records allows for changing the NS and A/AAAA glue records.

Marking a domain as "delegated" simply locks the domain in the web interface. The build scripts do not distinguish between delegated and un-delegated domains.

If you need to add a new record you must mark the domain as no longer "delegated" add the record and again mark the domain as "delegated".


Domain
------
.. automodule:: cyder.cydns.domain.models
    :members:
