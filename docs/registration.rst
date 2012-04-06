.. _registration:

Static Registrations
====================
A static registration allows a user to easily create an A/AAAA :class:`AddressRecord` record,
:class:`PTR` record, and optionally register the host in the DHCP configs.

A static registration takes a ``hostname``, ``ip`` and a ``mac`` and
generates DNS and DHCP entries. The DNS entries are an A/AAAA record and a PTR record::

    <hostname>      A     <ip>
    <ip>            PTR   <hostname>

The DHCP entry is a host clause::

    host <hostname> {
        fixed-address <ip>;
        hardware ethernet <mac>;
    }

These two constructions are not disjoint features in cyder. You can use the DNS portion of a
registration without using the DHCP portion. But, using the DHCP portion without using the DNS
portion is not supported. This is because the ``ip`` used in the DHCP portion of the construction is
stored in the created :class:`AddressRecord` and :class:`PTR` objects.

DNS
---
The DNS part of a registration creates an :class:`AddressRecord` object and a :class:`PTR`
object.  The creation of these two objects does not use the forms within the :ref:`address_record`
and :ref:`ptr` modules. Instead, special registration forms use the ``ip`` and ``hostname`` pair to build the
:class:`AddressRecord` and :class:`PTR` objects.

Deleting DNS registration objects
+++++++++++++++++++++++++++++++++
The objects created by the registration form are stored in default DNS tables. The objects are visible
to users when viewing DNS objects. Deleting objects that are tied to a registration via the details
view of an object is not allowed. To delete an object that is part of a registration you must delete
the entire registration.

Editing DNS registration objects
++++++++++++++++++++++++++++++++
Editing objects created by a registration is allowed.

DHCP
----
By choosing an ``ip`` you are in effect assigning the registration to a :class:`Range`.

Static Registration
-------------------
.. automodule:: cyder.core.registrations.models
    :members: StaticRegistration
